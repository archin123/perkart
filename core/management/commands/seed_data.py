import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, EmployeeVerification
from products.models import ProductCategory, Product, Offer
from faq.models import FAQCategory, FAQ
from troubleshooting.models import ErrorCode, AppErrorLog
from core.models import Feedback


class Command(BaseCommand):
    help = "Seeds the PerkCart corporate shopping platform with rich demonstration data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding PerkCart demonstration data..."))

        # 1. Create Superuser
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@perkcart.com",
                "first_name": "PerkCart",
                "last_name": "Administrator",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            admin_user.set_password("Admin@12345")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / Admin@12345"))
        
        # Ensure profile for admin
        profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        profile.company_name = "PerkCart HQ Global"
        profile.employee_id = "ADM-001"
        profile.corporate_email = "admin@perkcart.com"
        profile.verification_status = "APPROVED"
        profile.is_corporate_verified = True
        profile.save()

        # 2. Create Test Verified Employee User
        emp_user, created = User.objects.get_or_create(
            username="employee",
            defaults={
                "email": "employee@corporate.perkcart.com",
                "first_name": "Arjun",
                "last_name": "Sharma",
            }
        )
        if created:
            emp_user.set_password("PerkCart@2026")
            emp_user.save()
            self.stdout.write(self.style.SUCCESS("Created verified test employee: employee / PerkCart@2026"))
        
        emp_profile, _ = UserProfile.objects.get_or_create(user=emp_user)
        emp_profile.company_name = "Apex Global Technologies"
        emp_profile.employee_id = "EMP-94021"
        emp_profile.corporate_email = "arjun.sharma@apexcorp.internal"
        emp_profile.phone = "+91 98765 43210"
        emp_profile.department = "Enterprise Cloud Solutions"
        emp_profile.shipping_address = "Tower B, Level 8, Cyber City Tech Park, DLF Phase 2"
        emp_profile.city = "Gurugram"
        emp_profile.postal_code = "122002"
        emp_profile.verification_status = "APPROVED"
        emp_profile.is_corporate_verified = True
        emp_profile.save()

        # 3. Create Test Pending Intern User
        intern_user, created = User.objects.get_or_create(
            username="intern",
            defaults={
                "email": "intern@apexcorp.internal",
                "first_name": "Pooja",
                "last_name": "Nair",
            }
        )
        if created:
            intern_user.set_password("PerkCart@2026")
            intern_user.save()
            self.stdout.write(self.style.SUCCESS("Created pending test intern: intern / PerkCart@2026"))

        intern_profile, _ = UserProfile.objects.get_or_create(user=intern_user)
        intern_profile.company_name = "Apex Global Technologies"
        intern_profile.employee_id = "INT-3042"
        intern_profile.corporate_email = "pooja.nair@apexcorp.internal"
        intern_profile.verification_status = "PENDING"
        intern_profile.is_corporate_verified = False
        intern_profile.save()

        # Verification request
        EmployeeVerification.objects.get_or_create(
            user=intern_user,
            defaults={
                "company_name": "Apex Global Technologies",
                "corporate_email": "pooja.nair@apexcorp.internal",
                "employee_id": "INT-3042",
                "work_location": "Bengaluru Innovation Campus",
                "status": "PENDING",
                "admin_notes": "Submitted corporate badge photo for review."
            }
        )

        # 4. Product Categories
        categories_data = [
            {
                "name": "Laptops & Workstations",
                "slug": "laptops-workstations",
                "icon": "bi-laptop",
                "description": "High-performance enterprise ultrabooks, AI-ready laptops, and mobile workstations tailored for corporate power users.",
                "order": 1
            },
            {
                "name": "Flagship Smartphones",
                "slug": "flagship-smartphones",
                "icon": "bi-phone",
                "description": "Next-generation smartphones featuring dual-SIM corporate security, AI processing, and edge-to-edge AMOLED displays.",
                "order": 2
            },
            {
                "name": "Audio & ANC Headsets",
                "slug": "audio-anc-headsets",
                "icon": "bi-headphones",
                "description": "Industry-leading active noise cancelling headphones, wireless earbuds, and conference headsets for distraction-free work.",
                "order": 3
            },
            {
                "name": "Smart Displays & Monitors",
                "slug": "smart-displays-monitors",
                "icon": "bi-display",
                "description": "Ultra-wide curved productivity monitors, 4K studio displays, and USB-C single-cable docking screens.",
                "order": 4
            },
            {
                "name": "Smart Office & Wearables",
                "slug": "smart-office-wearables",
                "icon": "bi-smartwatch",
                "description": "Enterprise wellness smartwatches, ergonomic peripherals, and connected desktop accessories.",
                "order": 5
            },
            {
                "name": "Premium Tech Accessories",
                "slug": "premium-tech-accessories",
                "icon": "bi-usb-plug",
                "description": "Thunderbolt 4 docking stations, GaN fast chargers, precision ergonomic mice, and protective sleeves.",
                "order": 6
            },
        ]

        cat_objs = {}
        for c in categories_data:
            obj, _ = ProductCategory.objects.update_or_create(
                slug=c["slug"],
                defaults={
                    "name": c["name"],
                    "icon": c["icon"],
                    "description": c["description"],
                    "order": c["order"],
                    "is_active": True
                }
            )
            cat_objs[c["slug"]] = obj
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(cat_objs)} product categories."))

        # 5. Products (14 high-quality corporate products)
        products_data = [
            {
                "category": cat_objs["laptops-workstations"],
                "name": "PerkBook Ultra 16 Pro AI Workstation",
                "slug": "perkbook-ultra-16-pro-ai",
                "sku": "PB-ULTRA16-01",
                "tagline": "Flagship 16-inch 3.2K OLED workstation engineered with Intel Core Ultra 9 and neural processing unit.",
                "description": "The PerkBook Ultra 16 Pro is the definitive mobile computing benchmark for corporate software architects, data analysts, and executive leadership. Featuring an aerospace-grade aluminum chassis, 120Hz variable refresh rate OLED panel with 100% DCI-P3 color accuracy, and up to 18 hours of real-world battery endurance with single-cable Thunderbolt 4 fast charging.",
                "specs": {
                    "Processor": "Intel Core Ultra 9 185H (16 Cores, up to 5.1 GHz, Dual NPU)",
                    "RAM": "32GB LPDDR5X 7467 MHz Dual Channel",
                    "Storage": "1TB PCIe Gen4 NVMe M.2 High-Speed SSD",
                    "Display": "16.0-inch 3.2K (3200x2000) OLED 120Hz, 500 nits HDR",
                    "Graphics": "Intel Arc Graphics + Dedicated Intel AI Boost",
                    "Weight": "1.68 kg ultra-slim profile",
                    "Battery": "84Wh supporting 100W USB-C GaN Rapid Charge"
                },
                "original_price": Decimal("189999.00"),
                "corporate_price": Decimal("134999.00"),
                "stock_quantity": 35,
                "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1000&q=80",
                "badge": "Corporate Exclusive: Save 29%",
                "is_featured": True,
                "rating": Decimal("4.9"),
                "review_count": 86
            },
            {
                "category": cat_objs["laptops-workstations"],
                "name": "PerkBook Air Slim 14 Carbon",
                "slug": "perkbook-air-slim-14-carbon",
                "sku": "PB-AIR14-02",
                "tagline": "Featherlight 1.05 kg executive ultrabook with AMD Ryzen AI 9 and 22-hour battery life.",
                "description": "Crafted from structural carbon-fiber weave and magnesium alloy, the PerkBook Air Slim 14 delivers uncompromised performance for mobile professionals who travel frequently. Features a whisper-quiet thermal vapor chamber, enterprise fingerprint biometric authentication, and hardware-level webcam privacy shutter.",
                "specs": {
                    "Processor": "AMD Ryzen AI 9 HX 370 (12 Cores, 24 Threads, 50 TOPS NPU)",
                    "RAM": "16GB LPDDR5X High Efficiency RAM",
                    "Storage": "512GB PCIe Gen4 SSD",
                    "Display": "14.0-inch 2.8K IPS anti-glare, 100% sRGB, 450 nits",
                    "Weight": "1.05 kg ultra-portable",
                    "Connectivity": "Wi-Fi 7, Bluetooth 5.4, Dual USB4 Type-C"
                },
                "original_price": Decimal("129999.00"),
                "corporate_price": Decimal("94999.00"),
                "stock_quantity": 48,
                "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=1000&q=80",
                "badge": "Top Employee Choice",
                "is_featured": True,
                "rating": Decimal("4.8"),
                "review_count": 112
            },
            {
                "category": cat_objs["laptops-workstations"],
                "name": "Apex ThinkPro Enterprise X1",
                "slug": "apex-thinkpro-enterprise-x1",
                "sku": "AT-X1-03",
                "tagline": "Military-grade durability, spill-resistant ergonomic keyboard, and optional 5G eSIM connectivity.",
                "description": "Standardized by Fortune 500 IT departments worldwide, the Apex ThinkPro Enterprise X1 meets MIL-STD-810H durability standards. Includes hardware TPM 2.0 cryptographic chip, Kensington lock slot, and enterprise fleet remote management capabilities.",
                "specs": {
                    "Processor": "Intel Core Ultra 7 165U vPro Enterprise",
                    "RAM": "32GB DDR5 5600 MHz",
                    "Storage": "1TB Opal2 Encrypted SSD",
                    "Display": "14-inch WUXGA (1920x1200) Low Blue Light Touch",
                    "Security": "vPro, IR Camera with Windows Hello, Match-on-Chip Fingerprint",
                    "Durability": "MIL-STD-810H certified with spill-resistant trackpoint keyboard"
                },
                "original_price": Decimal("154999.00"),
                "corporate_price": Decimal("112999.00"),
                "stock_quantity": 22,
                "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=1000&q=80",
                "badge": "IT Fleet Certified",
                "is_featured": False,
                "rating": Decimal("4.7"),
                "review_count": 64
            },
            {
                "category": cat_objs["flagship-smartphones"],
                "name": "PerkPhone Horizon Z Fold 6 Enterprise",
                "slug": "perkphone-horizon-z-fold-6",
                "sku": "PH-FOLD6-04",
                "tagline": "Revolutionary 7.6-inch folding Dynamic AMOLED productivity powerhouse with multi-window multitasking.",
                "description": "Combine tablet multitasking with pocket portability. The PerkPhone Horizon Z Fold 6 Enterprise includes Knox-grade corporate security partition, support for precision stylus S-Pen, and desktop Dex mode for connecting directly to external monitors.",
                "specs": {
                    "Main Display": "7.6-inch QXGA+ Dynamic AMOLED 2X 120Hz Flex Screen",
                    "Cover Display": "6.3-inch Dynamic AMOLED 2X 120Hz",
                    "Processor": "Qualcomm Snapdragon 8 Gen 3 for Galaxy (4nm)",
                    "Memory": "12GB LPDDR5X RAM + 512GB UFS 4.0 Storage",
                    "Camera": "50MP Main + 12MP Ultra-Wide + 10MP 3x Optical Telephoto",
                    "Security": "Hardware Knox Vault, Biometric Dual-Key, Corporate Container"
                },
                "original_price": Decimal("164999.00"),
                "corporate_price": Decimal("121999.00"),
                "stock_quantity": 18,
                "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=1000&q=80",
                "badge": "Corporate Special: Save ₹43,000",
                "is_featured": True,
                "rating": Decimal("4.9"),
                "review_count": 73
            },
            {
                "category": cat_objs["flagship-smartphones"],
                "name": "PerkPhone Titanium Pro 6.7",
                "slug": "perkphone-titanium-pro-67",
                "sku": "PH-TITAN-05",
                "tagline": "Grade-5 titanium frame, studio-grade 50MP Sony sensor, and all-day 5400mAh intelligent silicon battery.",
                "description": "Built for executives who demand flawless photography, instantaneous app switching, and seamless battery reliability. Equipped with Corning Gorilla Armor anti-reflective glass, satellite emergency beacon connectivity, and 65W SuperVOOC flash charge.",
                "specs": {
                    "Processor": "Snapdragon 8 Gen 3 (3.3 GHz)",
                    "Display": "6.7-inch QHD+ 1-120Hz LTPO ProXDR, 4500 nits peak",
                    "RAM/Storage": "16GB RAM + 256GB High-Speed Storage",
                    "Battery": "5400 mAh dual-cell with 80W wired / 50W wireless",
                    "Audio": "Dual stereo speakers with Dolby Atmos spatial tuning"
                },
                "original_price": Decimal("89999.00"),
                "corporate_price": Decimal("64999.00"),
                "stock_quantity": 40,
                "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1000&q=80",
                "badge": "Save 28%",
                "is_featured": False,
                "rating": Decimal("4.8"),
                "review_count": 95
            },
            {
                "category": cat_objs["audio-anc-headsets"],
                "name": "SoundSilence Master Pro Wireless ANC",
                "slug": "soundsilence-master-pro-anc",
                "sku": "AUD-SSPRO-06",
                "tagline": "Industry-benchmark 45dB hybrid adaptive noise cancellation with 40-hour battery and carbon diaphragm.",
                "description": "Escape open-office chatter and aircraft engine rumble. Custom 40mm carbon biocellulose drivers reproduce crystal clear highs, rich mids, and defined low frequencies. Includes 8 precision beamforming microphones with AI background chatter cancellation for Zoom and Teams meetings.",
                "specs": {
                    "Noise Cancellation": "Dual-chip Hybrid Active Noise Cancellation (-45dB reduction)",
                    "Battery Life": "40 hours with ANC ON / 60 hours with ANC OFF",
                    "Quick Charge": "10 minutes charge yields 5 hours playback",
                    "Codecs": "LDAC, AAC, aptX Adaptive, SBC, Hi-Res Audio Certified",
                    "Multipoint": "Seamless dual Bluetooth 5.3 connection between laptop & phone"
                },
                "original_price": Decimal("29999.00"),
                "corporate_price": Decimal("18999.00"),
                "stock_quantity": 60,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1000&q=80",
                "badge": "Employee Best Seller",
                "is_featured": True,
                "rating": Decimal("4.9"),
                "review_count": 210
            },
            {
                "category": cat_objs["audio-anc-headsets"],
                "name": "PerkPods Spatial Studio Earbuds",
                "slug": "perkpods-spatial-studio-earbuds",
                "sku": "AUD-PPSPAT-07",
                "tagline": "Pocket-sized true wireless earbuds with dynamic head tracking, IPX5 water resistance, and wireless Qi case.",
                "description": "Designed for back-to-back corporate conference calls and evening fitness workouts. Features transparent awareness mode, capacitive touch stems, and magnetic wireless charging.",
                "specs": {
                    "Driver": "11mm custom dual-magnet dynamic driver",
                    "ANC Depth": "Up to 42dB smart adaptive noise suppression",
                    "Battery": "8 hours per charge + 28 hours with charging case",
                    "Water Resistance": "IPX5 sweat and splash protection",
                    "Microphones": "Triple mic array with wind-noise reduction mesh"
                },
                "original_price": Decimal("19999.00"),
                "corporate_price": Decimal("11999.00"),
                "stock_quantity": 75,
                "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=1000&q=80",
                "badge": "Save 40%",
                "is_featured": False,
                "rating": Decimal("4.7"),
                "review_count": 142
            },
            {
                "category": cat_objs["smart-displays-monitors"],
                "name": "UltraWide 34-inch Curved Productivity Display",
                "slug": "ultrawide-34-curved-display",
                "sku": "MON-UW34-08",
                "tagline": "1500R curved WQHD 3440x1440 IPS panel with 90W USB-C single cable dock and built-in KVM switch.",
                "description": "Replace dual messy monitors with one expansive panoramic canvas. The integrated KVM switch allows you to control your corporate laptop and personal desktop using one set of mouse and keyboard. Features 90W Power Delivery over USB Type-C to eliminate bulky laptop power bricks.",
                "specs": {
                    "Panel Size": "34.0 inches 21:9 UltraWide 1500R curvature",
                    "Resolution": "WQHD 3440 x 1440 @ 100Hz refresh rate",
                    "Color Gamut": "99% sRGB, HDR10, Delta E < 2 factory calibrated",
                    "Ports": "USB-C (90W PD, DisplayPort), 2x HDMI 2.0, 1x DP 1.4, 4x USB 3.2 hub, RJ45 Gigabit Ethernet",
                    "Stand": "Fully ergonomic height, tilt, and swivel adjustable stand"
                },
                "original_price": Decimal("59999.00"),
                "corporate_price": Decimal("39999.00"),
                "stock_quantity": 28,
                "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=1000&q=80",
                "badge": "Corporate Workspace Essential",
                "is_featured": True,
                "rating": Decimal("4.9"),
                "review_count": 68
            },
            {
                "category": cat_objs["smart-displays-monitors"],
                "name": "ViewStudio 27-inch 4K UHD Designer Monitor",
                "slug": "viewstudio-27-4k-uhd-monitor",
                "sku": "MON-VS27-09",
                "tagline": "Ultra-sharp 3840x2160 IPS panel with hardware calibration, 98% DCI-P3, and Daisy Chain support.",
                "description": "Ideal for UI/UX designers, developers, and data visualization specialists requiring pixel-perfect clarity. Equipped with anti-glare micro-texture coating and TÜV Rheinland certified low blue light emission.",
                "specs": {
                    "Resolution": "3840 x 2160 (4K UHD) at 60Hz",
                    "Color Depth": "1.07 Billion colors (10-bit), 98% DCI-P3",
                    "Brightness": "400 nits with VESA DisplayHDR 400",
                    "Inputs": "USB-C with 65W PD, DisplayPort 1.4 Out for daisy-chaining"
                },
                "original_price": Decimal("44999.00"),
                "corporate_price": Decimal("31999.00"),
                "stock_quantity": 30,
                "image_url": "https://images.unsplash.com/photo-1547082299-de196ea013d6?auto=format&fit=crop&w=1000&q=80",
                "badge": "Save 29%",
                "is_featured": False,
                "rating": Decimal("4.8"),
                "review_count": 52
            },
            {
                "category": cat_objs["smart-office-wearables"],
                "name": "TimePulse Enterprise Health Smartwatch",
                "slug": "timepulse-enterprise-health-smartwatch",
                "sku": "WR-TPENT-10",
                "tagline": "Titanium case smartwatch with medical-grade ECG, stress monitoring, sleep apnea detection, and 7-day battery.",
                "description": "Keep executive wellness and corporate productivity in sync. Receive prioritized enterprise calendar alerts, Microsoft Outlook and Slack notifications on your wrist, and monitor heart rate variability during demanding workweeks.",
                "specs": {
                    "Case Material": "Aerospace Grade 5 Titanium with sapphire crystal glass",
                    "Display": "1.43-inch Always-On AMOLED, 1000 nits outdoor brightness",
                    "Health Sensors": "Optical BioTracker 4.0, ECG, SpO2, Skin Temperature, Stress index",
                    "Battery": "7 to 10 days normal corporate usage on a single charge",
                    "Connectivity": "Bluetooth 5.3, NFC corporate door access compatible"
                },
                "original_price": Decimal("32999.00"),
                "corporate_price": Decimal("21999.00"),
                "stock_quantity": 45,
                "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=1000&q=80",
                "badge": "Wellness Partner Pick",
                "is_featured": False,
                "rating": Decimal("4.7"),
                "review_count": 89
            },
            {
                "category": cat_objs["smart-office-wearables"],
                "name": "DeskMaster Silent Ergonomic Mechanical Keyboard",
                "slug": "deskmaster-silent-ergonomic-mechanical-keyboard",
                "sku": "ACC-DMSIL-11",
                "tagline": "Custom pre-lubed silent switches, multi-device Bluetooth/2.4G pairing, and padded wrist rest.",
                "description": "Tactile typing precision without disrupting coworkers during open-office or hybrid conference calls. Hot-swappable PCB, double-shot PBT keycaps that never shine, and up to 5 months of battery life on smart power saving mode.",
                "specs": {
                    "Switches": "Custom Silent Linear Sea Salt Switches (45gf actuation)",
                    "Keycaps": "OEM Profile Double-Shot PBT, fade resistant",
                    "Battery": "4000mAh rechargeable lithium battery via USB-C",
                    "Connectivity": "Tri-mode (Bluetooth 5.1 x 3 devices, 2.4GHz USB Dongle, Type-C wired)"
                },
                "original_price": Decimal("11999.00"),
                "corporate_price": Decimal("7499.00"),
                "stock_quantity": 90,
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=1000&q=80",
                "badge": "Save 38%",
                "is_featured": False,
                "rating": Decimal("4.9"),
                "review_count": 134
            },
            {
                "category": cat_objs["premium-tech-accessories"],
                "name": "DeskMatrix 12-in-1 Thunderbolt 4 Enterprise Dock",
                "slug": "deskmatrix-12-in-1-thunderbolt-4-dock",
                "sku": "ACC-DMTB4-12",
                "tagline": "Power and connect your entire workspace with 180W power supply, dual 4K/single 8K output, and 2.5G LAN.",
                "description": "The enterprise standard for clean corporate hot-desking. Just plug one Thunderbolt cable into your laptop to instantly power dual displays, wired 2.5 Gigabit corporate intranet, studio microphones, SD cards, and high-speed external NVMe drives.",
                "specs": {
                    "Power Delivery": "Host charging up to 96W PD (180W DC Adapter included)",
                    "Video Ports": "2x Thunderbolt 4 down, 1x HDMI 2.1, 1x DisplayPort 1.4",
                    "Networking": "2.5 Gigabit Ethernet (RJ-45) with Wake-on-LAN and PXE boot support",
                    "Data Ports": "4x USB-A 3.2 Gen 2 (10Gbps), UHS-II SD & microSD card reader"
                },
                "original_price": Decimal("24999.00"),
                "corporate_price": Decimal("16499.00"),
                "stock_quantity": 38,
                "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?auto=format&fit=crop&w=1000&q=80",
                "badge": "Hot Desk Standard",
                "is_featured": True,
                "rating": Decimal("4.9"),
                "review_count": 57
            },
            {
                "category": cat_objs["premium-tech-accessories"],
                "name": "NeoGrip Precision Flow Wireless Mouse",
                "slug": "neogrip-precision-flow-wireless-mouse",
                "sku": "ACC-NEOGRIP-13",
                "tagline": "MagSpeed electromagnetic scroll wheel, 8000 DPI Darkfield glass tracking, and silent clicks.",
                "description": "Ergonomically sculpted to fit the natural contours of your hand. Seamlessly copy text, files, and images across up to three different computers using cross-OS Flow software.",
                "specs": {
                    "Sensor": "Darkfield High Precision 8000 DPI (tracks even on transparent glass)",
                    "Scroll Wheel": "MagSpeed Electromagnetic wheel (shifts from ratchet to hyper-fast free spin)",
                    "Buttons": "7 custom programmable buttons with gesture button",
                    "Battery": "Up to 70 days on a full charge, 3 hours from 1 minute rapid charge"
                },
                "original_price": Decimal("8999.00"),
                "corporate_price": Decimal("5499.00"),
                "stock_quantity": 85,
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=1000&q=80",
                "badge": "Save 39%",
                "is_featured": False,
                "rating": Decimal("4.8"),
                "review_count": 182
            },
            {
                "category": cat_objs["premium-tech-accessories"],
                "name": "MagnaCharge 3-in-1 Qi2 Rapid Wireless Stand",
                "slug": "magnacharge-3-in-1-qi2-rapid-stand",
                "sku": "ACC-MAGNA-14",
                "tagline": "Solid aerospace aluminum wireless stand charging phone (15W Qi2), smartwatch, and earbuds simultaneously.",
                "description": "Clean up your nightstand or office desk. Strong magnetic alignment holds your phone at optimal video-call angles in both portrait and landscape orientations while fast charging.",
                "specs": {
                    "Phone Charging": "15W Certified Qi2 magnetic fast charging",
                    "Watch Charging": "5W fast magnetic module for enterprise smartwatches",
                    "Earbuds Tray": "5W wireless pad with soft indent",
                    "Materials": "CNC machined aircraft aluminum with weighted non-slip base"
                },
                "original_price": Decimal("9999.00"),
                "corporate_price": Decimal("5999.00"),
                "stock_quantity": 55,
                "image_url": "https://images.unsplash.com/photo-1622445268047-975a593e2759?auto=format&fit=crop&w=1000&q=80",
                "badge": "Save 40%",
                "is_featured": False,
                "rating": Decimal("4.8"),
                "review_count": 91
            },
        ]

        for p_data in products_data:
            Product.objects.update_or_create(
                sku=p_data["sku"],
                defaults=p_data
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(products_data)} corporate products."))

        # 6. Corporate Offers / Coupons
        offers_data = [
            {
                "code": "WELCOME10",
                "title": "New Employee Welcome Privilege",
                "description": "10% additional corporate discount on your first PerkCart purchase after employee verification.",
                "discount_percent": 10,
                "max_discount_amount": Decimal("3000.00"),
                "min_order_amount": Decimal("5000.00"),
                "is_corporate_only": True,
                "is_active": True
            },
            {
                "code": "PERKTECH20",
                "title": "Enterprise Power Upgrade",
                "description": "Special 20% discount on workstations, curved monitors, and docking solutions.",
                "discount_percent": 20,
                "max_discount_amount": Decimal("15000.00"),
                "min_order_amount": Decimal("25000.00"),
                "is_corporate_only": True,
                "is_active": True
            },
            {
                "code": "CORPVIP",
                "title": "Corporate Tier-1 Partner Perk",
                "description": "Flat 15% exclusive allowance for registered corporate employees.",
                "discount_percent": 15,
                "max_discount_amount": Decimal("8000.00"),
                "min_order_amount": Decimal("10000.00"),
                "is_corporate_only": True,
                "is_active": True
            },
            {
                "code": "FREESHIP",
                "title": "Complimentary Expedited Delivery",
                "description": "Zero shipping fees and prioritized warehouse fulfillment for all tech accessories.",
                "discount_percent": 5,
                "max_discount_amount": Decimal("1000.00"),
                "min_order_amount": Decimal("2000.00"),
                "is_corporate_only": True,
                "is_active": True
            },
        ]

        for o in offers_data:
            Offer.objects.update_or_create(
                code=o["code"],
                defaults=o
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(offers_data)} corporate coupons."))

        # 7. FAQ Categories & FAQs (15 comprehensive questions across all 10 required domains)
        faq_cats_data = [
            {"name": "Registration & Verification", "slug": "registration-verification", "icon": "bi-person-check", "order": 1},
            {"name": "Corporate Discounts & Offers", "slug": "discounts-offers", "icon": "bi-tag", "order": 2},
            {"name": "Products & Specifications", "slug": "products-specs", "icon": "bi-laptop", "order": 3},
            {"name": "Shopping Cart & Checkout", "slug": "cart-checkout", "icon": "bi-cart3", "order": 4},
            {"name": "Orders & Corporate Delivery", "slug": "orders-delivery", "icon": "bi-truck", "order": 5},
            {"name": "Payments & Payroll Deduction", "slug": "payments-billing", "icon": "bi-credit-card", "order": 6},
            {"name": "Returns & Warranty", "slug": "returns-warranty", "icon": "bi-shield-check", "order": 7},
            {"name": "Account Security", "slug": "account-security", "icon": "bi-lock", "order": 8},
        ]

        faq_cat_objs = {}
        for fc in faq_cats_data:
            obj, _ = FAQCategory.objects.update_or_create(
                slug=fc["slug"],
                defaults={"name": fc["name"], "icon": fc["icon"], "order": fc["order"]}
            )
            faq_cat_objs[fc["slug"]] = obj

        faqs_data = [
            {
                "category": faq_cat_objs["registration-verification"],
                "question": "Who is eligible to purchase from PerkCart?",
                "answer": "PerkCart is an exclusive corporate employee shopping platform. Any full-time, contract, or intern employee with an active corporate email address from a recognized partner organization is eligible. Simply register using your corporate email address to unlock enterprise employee discounts.",
                "order": 1,
                "helpful_count": 84,
                "unhelpful_count": 2
            },
            {
                "category": faq_cat_objs["registration-verification"],
                "question": "How long does employee verification take?",
                "answer": "In our simulated demonstration environment, verification requests can be reviewed and approved immediately by an administrator through the Django Admin panel or the Verification Management dashboard. In production workflows, domain automated validation approves recognized email domains within minutes.",
                "order": 2,
                "helpful_count": 65,
                "unhelpful_count": 1
            },
            {
                "category": faq_cat_objs["registration-verification"],
                "question": "Can I use PerkCart if my employee status is still 'PENDING'?",
                "answer": "Yes! You can browse the complete product catalog, compare technical specifications, review exclusive discounts, and add items to your wishlist. However, finalizing order checkout requires your corporate profile to be in the 'APPROVED' state to guarantee corporate discount eligibility.",
                "order": 3,
                "helpful_count": 52,
                "unhelpful_count": 3
            },
            {
                "category": faq_cat_objs["discounts-offers"],
                "question": "How are PerkCart corporate prices calculated?",
                "answer": "PerkCart negotiates direct bulk-procurement agreements with tier-1 technology manufacturers. Prices listed under 'Corporate Price' reflect pre-negotiated corporate subsidies ranging from 20% to 45% below standard manufacturer suggested retail prices (MSRP).",
                "order": 1,
                "helpful_count": 98,
                "unhelpful_count": 4
            },
            {
                "category": faq_cat_objs["discounts-offers"],
                "question": "Can I stack corporate coupon codes with existing product discounts?",
                "answer": "Yes. Active promotional coupons (such as WELCOME10 or PERKTECH20) apply on top of the already reduced corporate prices during checkout, subject to minimum order thresholds and maximum discount caps.",
                "order": 2,
                "helpful_count": 76,
                "unhelpful_count": 5
            },
            {
                "category": faq_cat_objs["products-specs"],
                "question": "Are all products brand new with manufacturer warranty?",
                "answer": "All items sold on PerkCart are 100% brand new, factory sealed, and come accompanied by full official manufacturer warranties (typically 1 to 3 years depending on the equipment category). Invoices generated are valid for direct warranty claims.",
                "order": 1,
                "helpful_count": 89,
                "unhelpful_count": 2
            },
            {
                "category": faq_cat_objs["products-specs"],
                "question": "Can I request custom hardware configurations for enterprise laptops?",
                "answer": "Standard catalog models feature optimized configurations chosen for corporate productivity. For department bulk purchases (10+ units with specialized RAM or encryption drives), corporate procurement managers can contact our enterprise liaison via the Feedback form.",
                "order": 2,
                "helpful_count": 41,
                "unhelpful_count": 3
            },
            {
                "category": faq_cat_objs["cart-checkout"],
                "question": "Why did my cart quantity reset or show an error CART-001?",
                "answer": "PerkCart validates inventory in real time. If an item sells out while in your cart or if you request more units than the available warehouse stock, error code CART-001 or CART-002 will trigger with an option to adjust your quantity to available levels.",
                "order": 1,
                "helpful_count": 63,
                "unhelpful_count": 1
            },
            {
                "category": faq_cat_objs["orders-delivery"],
                "question": "Can orders be delivered directly to my home or only to my office desk?",
                "answer": "You may choose either your verified corporate office address or your personal residential address during checkout. All deliveries require OTP or signed delivery confirmation for security.",
                "order": 1,
                "helpful_count": 115,
                "unhelpful_count": 4
            },
            {
                "category": faq_cat_objs["orders-delivery"],
                "question": "How do I track my dispatched order?",
                "answer": "Once placed, visit the 'My Orders' section in your profile navigation. Each order displays a live tracking indicator, simulated carrier dispatch details, estimated delivery timeline, and a printable order receipt.",
                "order": 2,
                "helpful_count": 92,
                "unhelpful_count": 2
            },
            {
                "category": faq_cat_objs["payments-billing"],
                "question": "Does PerkCart collect real credit card information?",
                "answer": "No. PerkCart is configured with a secure simulated demonstration checkout. Payment methods including 'Corporate Payroll Deduction', 'Simulated Corporate Card', and 'Simulated Instant UPI' create genuine database orders and transaction logs without handling real credit card numbers.",
                "order": 1,
                "helpful_count": 140,
                "unhelpful_count": 1
            },
            {
                "category": faq_cat_objs["payments-billing"],
                "question": "How does Corporate Payroll Deduction work?",
                "answer": "When selected, the approved order amount is scheduled for automatic installment deduction over 3 to 6 monthly payroll cycles via your employer's HRMS integration, completely interest-free.",
                "order": 2,
                "helpful_count": 78,
                "unhelpful_count": 3
            },
            {
                "category": faq_cat_objs["returns-warranty"],
                "question": "What is the return policy for corporate purchases?",
                "answer": "Employees enjoy a hassle-free 14-day replacement window for any hardware defects or shipping damages. Equipment must be returned with all original packaging, accessories, and warranty cards.",
                "order": 1,
                "helpful_count": 67,
                "unhelpful_count": 2
            },
            {
                "category": faq_cat_objs["account-security"],
                "question": "What happens to my PerkCart account if I change companies?",
                "answer": "Your purchase history and warranty receipts remain linked to your registered profile. Upon joining another partner organization, update your corporate email under User Profile to submit a re-verification request.",
                "order": 1,
                "helpful_count": 48,
                "unhelpful_count": 2
            },
            {
                "category": faq_cat_objs["account-security"],
                "question": "How does PerkCart protect employee privacy?",
                "answer": "PerkCart adheres strictly to enterprise privacy protocols. Personal addresses, phone numbers, and orders are strictly isolated using server-side authorization—users can only ever view their own records.",
                "order": 2,
                "helpful_count": 59,
                "unhelpful_count": 1
            },
        ]

        for f_data in faqs_data:
            FAQ.objects.update_or_create(
                question=f_data["question"],
                defaults=f_data
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(faqs_data)} database FAQs."))

        # 8. Error Codes (9 structured error records matching Section 4)
        error_codes_data = [
            {
                "code": "AUTH-001",
                "title": "Invalid Login Credentials",
                "category": "AUTH",
                "severity": "MEDIUM",
                "description": "The corporate email or password provided does not match any active PerkCart account records.",
                "possible_causes": (
                    "Typo in corporate email address or password.\n"
                    "Account registered under a different email alias.\n"
                    "Password recently reset and not updated in password manager."
                ),
                "troubleshooting_steps": (
                    "1. Double check the spelling of your corporate email address.\n"
                    "2. Ensure Caps Lock is not enabled when entering your password.\n"
                    "3. If you have not yet created an account, click 'Register' to create one.\n"
                    "4. Contact your IT portal administrator if your corporate directory SSO is locked."
                ),
                "preventive_recommendations": (
                    "Use a password manager to securely autofill corporate credentials.\n"
                    "Bookmark the PerkCart login URL to avoid phishing clones."
                ),
                "action_url": "/accounts/login/",
                "action_label": "Return to Login"
            },
            {
                "code": "AUTH-002",
                "title": "Employee Verification Pending",
                "category": "AUTH",
                "severity": "HIGH",
                "description": "Your account registration has been created, but your corporate employee credentials have not yet been approved by the portal administrator.",
                "possible_causes": (
                    "Newly registered account awaiting administrator review.\n"
                    "Corporate work email not yet confirmed via verification token.\n"
                    "Submitted employee badge or ID number requires manual approval."
                ),
                "troubleshooting_steps": (
                    "1. Visit your User Profile to inspect your current verification status.\n"
                    "2. Confirm that your work email domain matches your employer's registered domain.\n"
                    "3. For college demonstration purposes, an administrator can approve your account instantly via the Admin Dashboard."
                ),
                "preventive_recommendations": (
                    "Submit verification requests during standard business hours for expedited approval.\n"
                    "Ensure your employee ID matches your official badge documentation."
                ),
                "action_url": "/accounts/profile/",
                "action_label": "Check Profile Status"
            },
            {
                "code": "CART-001",
                "title": "Product Unavailable / Out of Stock",
                "category": "CART",
                "severity": "MEDIUM",
                "description": "The item you attempted to add to your cart or order is currently out of stock at the regional fulfillment center.",
                "possible_causes": (
                    "High demand during promotional flash sale.\n"
                    "Warehouse inventory allocated to simultaneous corporate orders.\n"
                    "Product discontinued or awaiting seasonal model refresh."
                ),
                "troubleshooting_steps": (
                    "1. Remove or reduce the quantity of the out-of-stock item from your shopping cart.\n"
                    "2. Add the product to your Wishlist to receive notification when inventory is replenished.\n"
                    "3. Browse alternative models in the same product category."
                ),
                "preventive_recommendations": (
                    "Complete checkout promptly during high-demand corporate sale cycles.\n"
                    "Review product stock badges prior to placing large department orders."
                ),
                "action_url": "/cart/",
                "action_label": "View Shopping Cart"
            },
            {
                "code": "CART-002",
                "title": "Invalid Quantity Specified",
                "category": "CART",
                "severity": "LOW",
                "description": "The requested item quantity is invalid, zero, negative, or exceeds maximum allowable units per corporate order.",
                "possible_causes": (
                    "Entered zero or negative number in quantity field.\n"
                    "Requested quantity exceeds warehouse stock on hand.\n"
                    "Exceeded per-employee quota for subsidized hardware."
                ),
                "troubleshooting_steps": (
                    "1. Set item quantity to a positive integer between 1 and available stock limit.\n"
                    "2. Click the 'Update Cart' button to recalculate subtotals.\n"
                    "3. For orders exceeding 10 units, submit an enterprise bulk inquiry."
                ),
                "preventive_recommendations": (
                    "Use the plus (+) and minus (-) steppers to adjust item quantities safely."
                ),
                "action_url": "/cart/",
                "action_label": "Adjust Cart"
            },
            {
                "code": "DISC-001",
                "title": "Invalid or Expired Corporate Coupon",
                "category": "DISCOUNT",
                "severity": "LOW",
                "description": "The coupon code entered could not be validated or has expired.",
                "possible_causes": (
                    "Coupon code misspelled or typed with extra spaces.\n"
                    "Order total does not meet the coupon's minimum purchase threshold.\n"
                    "Promotional offer validity date has passed."
                ),
                "troubleshooting_steps": (
                    "1. Check the coupon code for typing errors (e.g. WELCOME10, PERKTECH20).\n"
                    "2. Verify that your cart subtotal meets the minimum order amount.\n"
                    "3. Check the active corporate offers banner on the PerkCart homepage."
                ),
                "preventive_recommendations": (
                    "Copy and paste coupon codes directly from the Perks & Offers page."
                ),
                "action_url": "/cart/",
                "action_label": "Review Coupons"
            },
            {
                "code": "ORDER-001",
                "title": "Order Not Found or Access Denied",
                "category": "ORDER",
                "severity": "HIGH",
                "description": "The requested order number could not be found or belongs to a different corporate user account.",
                "possible_causes": (
                    "Order number mistyped in the tracking search bar.\n"
                    "Order was placed under a different user account.\n"
                    "Server-side security rules blocked unauthorized access to another user's order."
                ),
                "troubleshooting_steps": (
                    "1. Navigate to 'My Orders' from your account menu to see all verified orders.\n"
                    "2. Confirm that you are logged into the correct corporate account.\n"
                    "3. Check your order confirmation email for the exact PKC order reference."
                ),
                "preventive_recommendations": (
                    "Always access orders through your authenticated User Profile dashboard."
                ),
                "action_url": "/cart/orders/",
                "action_label": "View My Orders"
            },
            {
                "code": "PAY-001",
                "title": "Payment Confirmation Unavailable",
                "category": "PAYMENT",
                "severity": "HIGH",
                "description": "The simulated corporate payment gateway encountered a timeout or verification refusal during checkout processing.",
                "possible_causes": (
                    "Corporate payroll deduction limit exceeded for the current quarter.\n"
                    "Simulated payment gateway timeout during validation.\n"
                    "Incomplete shipping or billing address details."
                ),
                "troubleshooting_steps": (
                    "1. Verify that all required shipping address fields are filled.\n"
                    "2. Try choosing an alternate simulated payment method (e.g. Simulated Corporate Card or UPI).\n"
                    "3. Retry placing the order after reviewing your cart summary."
                ),
                "preventive_recommendations": (
                    "Ensure your employee profile has complete contact and department information before checkout."
                ),
                "action_url": "/cart/checkout/",
                "action_label": "Retry Checkout"
            },
            {
                "code": "API-001",
                "title": "Temporary Service Interruption",
                "category": "API",
                "severity": "CRITICAL",
                "description": "An internal service or external AI processing endpoint experienced a momentary timeout or connection latency.",
                "possible_causes": (
                    "AI assistant API rate limit reached or network latency.\n"
                    "Database connection pool refresh.\n"
                    "Background worker task synchronization delay."
                ),
                "troubleshooting_steps": (
                    "1. Wait 30 seconds and refresh the page.\n"
                    "2. The AI assistant automatically engages its intelligent search-based fallback engine if external generative APIs are unavailable.\n"
                    "3. Check our System Health & Operational Status page."
                ),
                "preventive_recommendations": (
                    "The system automatically fails over gracefully without data loss."
                ),
                "action_url": "/status/",
                "action_label": "Check System Status"
            },
            {
                "code": "SEC-001",
                "title": "Unauthorized Administrative Action Attempted",
                "category": "SECURITY",
                "severity": "CRITICAL",
                "description": "An operation requiring staff or superuser privileges was attempted by an unprivileged corporate user.",
                "possible_causes": (
                    "Attempting to access Django Admin or verification approval endpoints without staff credentials.\n"
                    "Expired administrator session.\n"
                    "Direct URL parameter tampering."
                ),
                "troubleshooting_steps": (
                    "1. Return to the standard employee store catalog.\n"
                    "2. If you are a platform evaluator or professor, log in using the superuser credentials (admin / Admin@12345).\n"
                    "3. Ensure your user account is marked 'is_staff' in Django."
                ),
                "preventive_recommendations": (
                    "Administrative actions are strictly audited and restricted server-side."
                ),
                "action_url": "/accounts/login/",
                "action_label": "Admin Login"
            },
        ]

        for ec_data in error_codes_data:
            ErrorCode.objects.update_or_create(
                code=ec_data["code"],
                defaults=ec_data
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(error_codes_data)} error codes."))

        # 9. Sample Feedback
        feedback_samples = [
            {
                "name": "Kavita Sen",
                "email": "kavita.sen@apexcorp.internal",
                "company_name": "Apex Global Technologies",
                "category": "EXPERIENCE",
                "rating": 5,
                "subject": "Exceptional employee store experience and smooth UI",
                "message": "The corporate discounts on the PerkBook Ultra 16 Pro saved our engineering team nearly 30% compared to retail. The interface looks remarkably sleek and responsive.",
                "is_reviewed": True,
                "admin_response": "Thank you Kavita! We are glad PerkCart is empowering your engineering team."
            },
            {
                "name": "Rahul Verma",
                "email": "rahul.v@infonet.corporate",
                "company_name": "InfoNet Global Systems",
                "category": "DISCOUNT",
                "rating": 4,
                "subject": "Great discounts on monitors",
                "message": "Purchased the 34-inch curved monitor using the WELCOME10 coupon. The single cable USB-C docking works perfectly with my work laptop.",
                "is_reviewed": True,
                "admin_response": "Glad to hear Rahul! Enjoy the ultra-wide productivity boost."
            }
        ]

        for fb in feedback_samples:
            Feedback.objects.get_or_create(
                email=fb["email"],
                subject=fb["subject"],
                defaults=fb
            )
        self.stdout.write(self.style.SUCCESS("Loaded sample employee feedback."))

        # 10. Sample Error Log (for demonstration)
        AppErrorLog.objects.get_or_create(
            error_code="CART-001",
            path="/cart/add/12/",
            message="Product inventory threshold notice: Item stock adjusted for demo checkout.",
            context_data="Simulation test record generated during system seeding."
        )

        self.stdout.write(self.style.SUCCESS("PerkCart demonstration data successfully seeded!"))
