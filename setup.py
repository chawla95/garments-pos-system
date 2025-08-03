from setuptools import setup, find_packages

setup(
    name="garments-pos-system",
    version="1.0.0",
    description="Garments POS System Backend",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "pydantic==2.7.0",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "reportlab==4.0.7",
        "python-barcode==0.15.1",
        "Pillow==10.4.0",
        "jinja2==3.1.2",
        "pandas==2.3.0",
        "numpy==1.26.4",
        "requests==2.31.0",
        "python-dateutil==2.8.2",
        "cryptography==42.0.0",
        "bcrypt==4.1.2"
    ],
    python_requires=">=3.10",
) 