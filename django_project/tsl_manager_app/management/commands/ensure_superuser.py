import os
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


def read_secret(path: str | None) -> str | None:
    if not path:
        return None
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise CommandError(f"Secret file not found: {path}")
    except PermissionError:
        raise CommandError(f"Secret file not readable: {path}")


class Command(BaseCommand):
    help = "Create/update default superuser from env/secrets."

    def handle(self, *args: Any, **options: Any) -> None:
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")

        password = read_secret(os.getenv("DJANGO_SUPERUSER_PASSWORD_FILE")) or os.getenv("DJANGO_SUPERUSER_PASSWORD")
        if not password:
            raise CommandError(
                "No superuser password provided. " "Set DJANGO_SUPERUSER_PASSWORD_FILE or DJANGO_SUPERUSER_PASSWORD."
            )

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_superuser": True, "is_staff": True},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created superuser {username}"))
        else:
            changed = False
            if user.email != email:
                user.email = email
                changed = True
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                changed = True
            if changed:
                user.save(update_fields=["email", "is_superuser", "is_staff"])
            self.stdout.write(f"Superuser {username} exists; ensuring credentials.")

        user.set_password(password)
        user.save(update_fields=["password"])
        self.stdout.write(self.style.SUCCESS("Superuser password set/updated."))
