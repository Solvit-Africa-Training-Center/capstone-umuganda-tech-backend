from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.core.files.base import ContentFile
from django.conf import settings
from io import BytesIO
import os
from .models import Attendance
from apps.users.models import Badge, UserBadge


class CertificateService:
    @staticmethod
    def create_placeholder_logos():
        """Create placeholder logos if they don't exist"""
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
        os.makedirs(static_dir, exist_ok=True)
        
        # Rwanda coat placeholder
        rwanda_seal_path = os.path.join(static_dir, 'Coat.png')
        if not os.path.exists(rwanda_seal_path):
            CertificateService._create_rwanda_seal_placeholder(rwanda_seal_path)
        
        # Umuganda logo placeholder  
        umuganda_logo_path = os.path.join(static_dir, 'umuganda_logo.png')
        if not os.path.exists(umuganda_logo_path):
            CertificateService._create_umuganda_placeholder(umuganda_logo_path)
        
        return rwanda_seal_path, umuganda_logo_path

    @staticmethod
    def _create_rwanda_seal_placeholder(path):
        """Create Rwanda Coat placeholder"""
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (120, 120), 'white')
        draw = ImageDraw.Draw(img)
        
        # Outer green ring
        draw.ellipse([5, 5, 115, 115], outline='#00A651', width=4)
        
        # Inner elements - simplified coat
        draw.ellipse([25, 25, 95, 95], fill='#00A1DE', outline='#006400', width=2)
        draw.rectangle([35, 45, 85, 75], fill='#00A651')
        
        # Gear representation
        for i in range(8):
            angle = i * 45
            x = 60 + 15 * (i % 2)
            y = 60 + 15 * ((i + 1) % 2)
            draw.ellipse([x-3, y-3, x+3, y+3], fill='#FAD201')
        
        img.save(path, 'PNG')

    @staticmethod
    def _create_umuganda_placeholder(path):
        """Create Umuganda community placeholder"""
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (120, 120), 'white')
        draw = ImageDraw.Draw(img)
        
        # Green circle for community
        draw.ellipse([10, 10, 110, 110], fill='#00A651', outline='#006400', width=3)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        draw.text((60, 60), "U", fill='white', font=font, anchor='mm')
        
        img.save(path, 'PNG')

    @staticmethod
    def generate_pdf(certificate):
        rwanda_seal_path, umuganda_logo_path = CertificateService.create_placeholder_logos()
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # --- Border ---
        p.setStrokeColor(colors.HexColor("#006400"))
        p.setLineWidth(4)
        p.rect(30, 30, width-60, height-60)

        # --- Rwanda Coat (top left) ---
        logo_size = 1.2*inch
        if os.path.exists(rwanda_seal_path):
            p.drawImage(rwanda_seal_path, 60, height-1.8*inch, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')
        
        # --- Umuganda Logo (top right) ---
        if os.path.exists(umuganda_logo_path):
            p.drawImage(umuganda_logo_path, width-60-logo_size, height-1.8*inch, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')

        # --- Header ---
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width/2, height-1.0*inch, "REPUBLIC OF RWANDA")
        p.setFont("Helvetica", 13)
        p.drawCentredString(width/2, height-1.3*inch, "UMUGANDA - National Community Service Program")

        # --- Certificate Title ---
        p.setFont("Helvetica-Bold", 28)
        p.setFillColor(colors.HexColor("#7d0a0a"))
        p.drawCentredString(width/2, height-2.5*inch, "CERTIFICATE OF PARTICIPATION")
        p.setFillColor(colors.black)

        # --- Recipient Name ---
        user_name = f"{certificate.user.first_name or ''} {certificate.user.last_name or ''}".strip() or certificate.user.phone_number
        p.setFont("Helvetica-Bold", 22)
        p.drawCentredString(width/2, height-3.7*inch, user_name)

        # --- Body text ---
        p.setFont("Helvetica", 14)
        text = (
            f"This certificate is proudly presented to {user_name},\n"
            f"for actively contributing to Umuganda and supporting community development\n"
            f"through the project: {certificate.project.title}."
        )
        for i, line in enumerate(text.split("\n")):
            p.drawCentredString(width/2, height-4.7*inch - (i*18), line)

        # --- Date ---
        p.setFont("Helvetica-Oblique", 12)
        p.drawCentredString(width/2, height-6.2*inch, f"Date: {certificate.project.datetime.strftime('%B %d, %Y')}")

        # --- Official Seal of Rwanda ---
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(width/2, height-7.5*inch, "REPUBLIC OF RWANDA")
        p.setFont("Helvetica", 10)

        # --- Single Signature Line ---
        p.line(width/3, height-8.5*inch, 2*width/3, height-8.5*inch)

        # --- Project creator signature as Local Authority/Community Leader ---
        project_creator_name = f"{certificate.project.admin.first_name or ''} {certificate.project.admin.last_name or ''}".strip()
        if not project_creator_name:
            project_creator_name = certificate.project.admin.phone_number

        p.setFont("Helvetica", 12)
        p.drawCentredString(width/2, height-8.8*inch, project_creator_name)
        p.setFont("Helvetica", 10)
        p.drawCentredString(width/2, height-9.1*inch, "Local Authority / Community Leader")

        # Finalize
        p.showPage()
        p.save()

        filename = f'certificate_{certificate.user.id}_{certificate.project.id}.pdf'
        certificate.certificate_file.save(filename, ContentFile(buffer.getvalue()))
        buffer.close()

        return certificate


class GamificationService:
    BADGE_SIZE = 150
    GRADIENT_STEPS = 5
    ALPHA_STEP = 30
    
    @staticmethod
    def create_default_badges():
        if Badge.objects.filter(name__in=["First Timer", "Regular Contributor", "Community Champion"]).exists():
            return
            
        GamificationService._create_badge_images()
        
        badges = [
            {
                "name": "First Timer", 
                "description": "Completed your first Umuganda project",
                "icon_url": "/static/images/badges/first_timer.png"
            },
            {
                "name": "Regular Contributor", 
                "description": "Completed 5 projects",
                "icon_url": "/static/images/badges/regular_contributor.png"
            },
            {
                "name": "Community Champion", 
                "description": "Completed 10+ projects",
                "icon_url": "/static/images/badges/community_champion.png"
            },
        ]
        
        for badge_data in badges:
            Badge.objects.get_or_create(
                name=badge_data["name"], 
                defaults={
                    "description": badge_data["description"],
                    "icon_url": badge_data["icon_url"]
                }
            )
    
    @staticmethod
    def _create_badge_images():
        from PIL import Image, ImageDraw
        
        badges_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'badges')
        os.makedirs(badges_dir, exist_ok=True)
        
        badges = [
            {"name": "first_timer", "color": "#4CAF50", "icon": "star"},
            {"name": "regular_contributor", "color": "#2196F3", "icon": "trophy"},
            {"name": "community_champion", "color": "#9C27B0", "icon": "crown"}
        ]
        
        for badge in badges:
            badge_path = os.path.join(badges_dir, f"{badge['name']}.png")
            if not os.path.exists(badge_path):
                GamificationService._create_badge(badge_path, badge)

    @staticmethod
    def _create_badge(path, config):
        from PIL import Image, ImageDraw
        
        img = None
        try:
            img = Image.new('RGBA', (GamificationService.BADGE_SIZE, GamificationService.BADGE_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            for i in range(GamificationService.GRADIENT_STEPS):
                alpha = 255 - i * GamificationService.ALPHA_STEP
                color = (*ImageDraw.ImageColor.getrgb(config["color"]), alpha)
                draw.ellipse([10-i, 10-i, 140+i, 140+i], fill=color)
            
            draw.ellipse([25, 25, 125, 125], fill='white', outline=config["color"], width=3)
            draw.ellipse([20, 20, 130, 130], outline='#FFD700', width=2)
            
            if config["icon"] == "star":
                GamificationService._draw_star(draw, 75, 75, 20, config["color"])
            elif config["icon"] == "trophy":
                GamificationService._draw_trophy(draw, 75, 75, config["color"])
            elif config["icon"] == "crown":
                GamificationService._draw_crown(draw, 75, 75, config["color"])
            
            img.save(path, 'PNG')
        finally:
            if img:
                img.close()

    @staticmethod
    def _draw_star(draw, cx, cy, size, color):
        import math
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = size if i % 2 == 0 else size * 0.4
            x = cx + radius * math.cos(angle - math.pi/2)
            y = cy + radius * math.sin(angle - math.pi/2)
            points.append((x, y))
        draw.polygon(points, fill=color)

    @staticmethod
    def _draw_trophy(draw, cx, cy, color):
        draw.ellipse([cx-15, cy-20, cx+15, cy-5], fill=color)
        draw.rectangle([cx-20, cy-5, cx+20, cy+5], fill=color)
        draw.rectangle([cx-10, cy+5, cx+10, cy+15], fill=color)
        draw.arc([cx-25, cy-15, cx-10, cy+5], outline=color, width=3)
        draw.arc([cx+10, cy-15, cx+25, cy+5], outline=color, width=3)

    @staticmethod
    def _draw_crown(draw, cx, cy, color):
        points = [(cx-20, cy+5), (cx-10, cy-15), (cx, cy-5), (cx+10, cy-20), (cx+20, cy+5)]
        draw.polygon(points, fill=color)
        draw.rectangle([cx-20, cy+5, cx+20, cy+15], fill=color)
        draw.ellipse([cx-2, cy-10, cx+2, cy-6], fill='#FFD700')

    @staticmethod
    def award_badges(user):
        if not Badge.objects.filter(name="First Timer").exists():
            GamificationService.create_default_badges()
            
        completed_count = Attendance.objects.filter(user=user, check_out_time__isnull=False).count()
        
        badge_thresholds = [(1, "First Timer"), (5, "Regular Contributor"), (10, "Community Champion")]
        awarded_badges = []
        
        for threshold, badge_name in badge_thresholds:
            if completed_count >= threshold:
                try:
                    badge = Badge.objects.get(name=badge_name)
                    user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)
                    if created:
                        awarded_badges.append(badge)
                except Badge.DoesNotExist:
                    continue
        
        return awarded_badges
