import os
import re
import html
import sqlite3


DB = "users.db"


def get_project_data(project_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT business_name, description
        FROM projects
        WHERE id = ?
        """,
        (project_id,)
    )

    project = cursor.fetchone()

    if not project:
        conn.close()
        return None

    business_name, description = project

    cursor.execute(
        """
        SELECT field_name, field_value
        FROM project_fields
        WHERE project_id = ?
        """,
        (project_id,)
    )

    fields = dict(cursor.fetchall())

    conn.close()

    return {
        "business_name": business_name or "My Business",
        "description": description or "",
        "phone": fields.get("phone"),
        "whatsapp": fields.get("whatsapp"),
        "email": fields.get("email"),
        "location": fields.get("location"),
        "services": fields.get("services"),
        "about": fields.get("about"),
        "logo": fields.get("logo"),
    }


def clean_phone(value):
    if not value:
        return ""

    return re.sub(r"[^0-9+]", "", value)


def prepare_services(value):
    if not value:
        return [
            "Quality Products",
            "Professional Service",
            "Customer Support"
        ]

    text = value.strip()

    # Allow customers to separate services with commas,
    # semicolons, or new lines.
    parts = re.split(r"[,;\n]+", text)

    services = []

    for part in parts:
        part = part.strip()

        if part:
            services.append(part)

    if not services:
        services = [
            "Quality Products",
            "Professional Service",
            "Customer Support"
        ]

    return services[:6]


def generate_website(description, job_id, project_id=None):

    # Use the structured project when available
    project = None

    if project_id:
        project = get_project_data(project_id)

    if project:
        business_name = project["business_name"]

        if business_name.lower().startswith("business:"):
               business_name = business_name.split(":", 1)[1].strip()
        phone = project["phone"]
        whatsapp = project["whatsapp"]
        email = project["email"]
        location = project["location"]
        services = project["services"]
        about = project["about"]
        logo = project["logo"]
    else:
        # Backward compatibility with old jobs
        business_name = "My Business"

        match = re.search(
            r"Business name:\s*(.+)",
            description or "",
            re.IGNORECASE
        )

        if match:
            business_name = match.group(1).strip()

        phone = None
        whatsapp = None
        email = None
        location = None
        services = None
        about = None
        logo = None

    business_name = business_name or "My Business"

    safe_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        business_name
    ).strip("_")

    if not safe_name:
        safe_name = f"website_{job_id}"

    folder = os.path.join(
        "generated_sites",
        f"{safe_name}_{job_id}"
    )

    os.makedirs(folder, exist_ok=True)

    logo_filename = None

    if logo and os.path.isfile(logo):
        logo_filename = "logo.jpg"

        with open(logo, "rb") as source:
            with open(
                os.path.join(folder, logo_filename),
                "wb"
            ) as destination:
                destination.write(source.read())

    safe_business_name = html.escape(
        business_name
    )

    if phone and phone.lower().startswith("phone:"):
           phone = phone.split(":", 1)[1].strip()

    safe_phone = html.escape(
        phone or "Will be added later"
    )

    safe_email = html.escape(
        email or "Will be added later"
    )

    safe_location = html.escape(
        location or "Will be added later"
    )

    service_items = prepare_services(services)

    safe_services = html.escape(
        services or
        "Quality products and professional services."
    )

    safe_about = html.escape(
        about or
        f"{business_name} provides quality products and services."
    )

    services_html = ""

    icons = ["★", "✓", "◆", "●", "✦", "➜"]

    for index, service in enumerate(service_items):
        icon = icons[index % len(icons)]

        service_lower = service.lower()

        if "web" in service_lower or "design" in service_lower:
            service_description = (
                "Professional website design with "
                "responsive layouts and a modern user experience."
            )
        elif "cyber" in service_lower or "security" in service_lower:
            service_description = (
                "Security-focused solutions designed to "
                "help protect systems, data, and digital operations."
            )
        elif "support" in service_lower or "it" in service_lower:
            service_description = (
                "Reliable technical support and practical "
                "IT solutions to keep your business running smoothly."
            )
        else:
            service_description = (
                "Professional service focused on quality, "
                "reliability, and customer satisfaction."
            )

        services_html += f"""
<div class="card">

<div class="card-icon">
{icon}
</div>

<h3>
{html.escape(service)}
</h3>

<p>
{html.escape(service_description)}
</p>

</div>
"""

    whatsapp_number = clean_phone(whatsapp)

    if whatsapp_number:
        whatsapp_url = (
            f"https://wa.me/{whatsapp_number.lstrip('+')}"
        )
    else:
        whatsapp_url = "#contact"

    if logo_filename:
        logo_html = """
    <div class="logo-container">
        <img src="./logo.jpg" alt="Business Logo">
    </div>
    """
    else:
        logo_html = ""

    page = f"""<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>{safe_business_name}</title>

<style>

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    font-family:
        Arial,
        Helvetica,
        sans-serif;
    line-height: 1.6;
    color: #1f2937;
    background: #f8fafc;
}}

a {{
    text-decoration: none;
}}

header {{
    position: sticky;
    top: 0;
    z-index: 1000;

    background:
        rgba(15, 23, 42, 0.96);

    color: white;

    padding: 16px 5%;

    box-shadow:
        0 4px 20px rgba(0,0,0,0.15);
}}

.header-inner {{
    max-width: 1200px;
    margin: auto;

    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 25px;
}}

.brand {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.logo-container {{
    display: flex;
    align-items: center;
}}

.logo-container img {{
    width: 58px;
    height: 58px;

    object-fit: contain;

    background: white;

    padding: 4px;

    border-radius: 12px;

    box-shadow:
        0 4px 15px rgba(0,0,0,0.2);
}}

.brand-name {{
    font-size: 20px;
    font-weight: 700;
    color: white;
}}

nav {{
    display: flex;
    align-items: center;
    gap: 22px;
}}

nav a {{
    color: #e5e7eb;
    font-size: 15px;
    font-weight: 600;

    transition:
        color 0.2s ease;
}}

nav a:hover {{
    color: #60a5fa;
}}

.hero {{
    min-height: 650px;

    display: flex;
    align-items: center;

    background:
        linear-gradient(
            135deg,
            #0f172a,
            #1e3a8a
        );

    color: white;

    padding: 90px 5%;
}}

.hero-content {{
    width: 100%;
    max-width: 1200px;
    margin: auto;
}}

.hero-badge {{
    display: inline-block;
    margin-bottom: 20px;
    padding: 8px 14px;
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    color: #bfdbfe;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

.hero-content h1 {{
    max-width: 800px;

    font-size:
        clamp(42px, 7vw, 76px);

    line-height: 1.05;

    margin-bottom: 25px;
}}

.hero-content p {{
    max-width: 700px;

    font-size: 19px;

    color: #dbeafe;

    margin-bottom: 30px;
}}

.button {{
    display: inline-block;

    padding: 14px 26px;

    border-radius: 10px;

    background: #2563eb;

    color: white;

    font-weight: 700;

    transition:
        transform 0.2s ease,
        background 0.2s ease;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.2);
}}

.button:hover {{
    background: #1d4ed8;

    transform:
        translateY(-2px);
}}

.button-secondary {{
    margin-left: 10px;
    background: transparent;
    border: 1px solid rgba(255,255,255,0.35);
}}

.button-secondary:hover {{
    background: rgba(255,255,255,0.10);
}}

.section {{
    max-width: 1200px;

    margin: auto;

    padding:
        90px 5%;
}}

.section-title {{
    text-align: center;

    margin-bottom: 45px;
}}

.section-title h2 {{
    font-size: 38px;

    color: #0f172a;

    margin-bottom: 10px;
}}

.section-title p {{
    color: #64748b;

    max-width: 650px;

    margin: auto;
}}

.cards {{
    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(250px, 1fr)
        );

    gap: 25px;
}}

.card {{
    position: relative;

    background: white;

    padding: 32px;

    border-radius: 18px;

    border:
        1px solid #e5e7eb;

    box-shadow:
        0 12px 30px rgba(15,23,42,0.07);

    overflow: hidden;

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease;
}}

.card::before {{
    content: "";

    position: absolute;

    top: 0;
    left: 0;

    width: 100%;
    height: 4px;

    background:
        linear-gradient(
            90deg,
            #2563eb,
            #60a5fa
        );
}}

.card:hover {{
    transform:
        translateY(-8px);

    box-shadow:
        0 20px 45px rgba(15,23,42,0.13);
}}

.card-icon {{
    width: 50px;
    height: 50px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 12px;

    background: #dbeafe;

    color: #1d4ed8;

    font-size: 23px;

    margin-bottom: 18px;
}}

.card h3 {{
    color: #0f172a;

    font-size: 21px;

    margin-bottom: 10px;
}}

.card p {{
    color: #64748b;
}}

.about {{
    background: #eef2ff;
}}

.about-box {{
    max-width: 900px;

    margin: auto;

    background: white;

    padding: 40px;

    border-radius: 18px;

    box-shadow:
        0 10px 35px rgba(15,23,42,0.08);
}}

.about-box p {{
    color: #475569;

    font-size: 17px;
}}

.contact {{
    background: #0f172a;

    color: white;
}}

.contact .section-title h2 {{
    color: white;
}}

.contact .section-title p {{
    color: #cbd5e1;
}}

.contact-box {{
    max-width: 900px;

    margin: auto;

    background: #1e293b;

    padding: 35px;

    border-radius: 18px;

    display: grid;

    gap: 20px;
}}

.contact-item {{
    display: flex;

    align-items: flex-start;

    gap: 15px;
}}

.contact-item strong {{
    display: block;

    color: white;

    margin-bottom: 3px;
}}

.contact-item span {{
    color: #cbd5e1;
}}

.contact-actions {{
    display: flex;

    flex-wrap: wrap;

    gap: 12px;

    margin-top: 10px;
}}

.whatsapp {{
    background: #16a34a;
}}

.whatsapp:hover {{
    background: #15803d;
}}

footer {{
    background: #020617;

    color: #94a3b8;

    text-align: center;

    padding: 30px 20px;
}}

footer strong {{
    color: white;
}}

@media (max-width: 700px) {{

    header {{
        padding: 12px 5%;
    }}

    .header-inner {{
        flex-direction: column;

        align-items: center;
    }}

    nav {{
        flex-wrap: wrap;

        justify-content: center;

        gap: 12px;
    }}

    .hero {{
        min-height: 560px;

        text-align: center;

        padding:
            70px 5%;
    }}

    .hero-content p {{
        margin-left: auto;
        margin-right: auto;
    }}

    .section {{
        padding:
            65px 5%;
    }}

    .section-title h2 {{
        font-size: 32px;
    }}

    .about-box,
    .contact-box {{
        padding: 25px;
    }}

}}

</style>
</head>

<body>

<header>

<div class="header-inner">

<div class="brand">

{logo_html}

<div class="brand-name">
{safe_business_name}
</div>

</div>

<nav>

<a href="#home">Home</a>

<a href="#services">
Services
</a>

<a href="#about">
About
</a>

<a href="#contact">
Contact
</a>

</nav>

</div>

</header>


<section id="home" class="hero">

<div class="hero-content">

<div class="hero-badge">
Professional Business
</div>

<h1>
{safe_business_name}
</h1>

<p>
{safe_services}
</p>

<a
    class="button"
    href="#contact">
Contact Us
</a>

<a
    class="button button-secondary"
    href="#services">
View Services
</a>

</div>

</section>


<section id="services" class="section">

<div class="section-title">

<h2>
Our Services
</h2>

<p>
Professional products and services
designed around our customers' needs.
</p>

</div>


<div class="cards">

{services_html}

</div>

</section>


<section id="about" class="about">

<div class="section">

<div class="section-title">

<h2>
About Us
</h2>

<p>
Learn more about {safe_business_name}.
</p>

</div>


<div class="about-box">

<p>
{safe_about}
</p>

</div>

</div>

</section>


<section id="contact" class="contact">

<div class="section">

<div class="section-title">

<h2>
Contact Us
</h2>

<p>
Get in touch with {safe_business_name}.
</p>

</div>


<div class="contact-box">

<div class="contact-item">

<div>
📞
</div>

<div>

<strong>
Phone
</strong>

<span>
{safe_phone}
</span>

</div>

</div>


<div class="contact-item">

<div>
✉️
</div>

<div>

<strong>
Email
</strong>

<span>
{safe_email}
</span>

</div>

</div>


<div class="contact-item">

<div>
📍
</div>

<div>

<strong>
Location
</strong>

<span>
{safe_location}
</span>

</div>

</div>


<div class="contact-actions">

<a
    class="button whatsapp"
    href="{whatsapp_url}">
WhatsApp Us
</a>

<a
    class="button"
    href="mailto:{safe_email}">
Send Email
</a>

</div>

</div>

</div>

</section>


<footer>

<p>
© 2026
<strong>
{safe_business_name}
</strong>.
All rights reserved.
</p>

<p>
Website generated by CyberQueen AI
</p>

</footer>

</body>

</html>
"""


    filepath = os.path.join(
        folder,
        "index.html"
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(page)

    return folder, filepath
