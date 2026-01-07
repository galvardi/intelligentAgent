from setuptools import setup, find_packages

# Find all packages but exclude venv
packages = [pkg for pkg in find_packages() if not pkg.startswith('venv')]

setup(
    name="intelligent-agent",
    version="0.1.0",
    packages=["intelligentAgent"] + [f"intelligentAgent.{pkg}" for pkg in packages],
    package_dir={"intelligentAgent": "."},
    install_requires=[
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.9",
)

