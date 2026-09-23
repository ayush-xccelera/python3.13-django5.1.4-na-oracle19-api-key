from django.core.management.base import BaseCommand

from notes.models import ApiKey, Note


class Command(BaseCommand):
    help = 'Seed the database with sample API keys and notes (idempotent).'

    def handle(self, *args, **options):
        key_names = ['Seed Client Alpha', 'Seed Client Beta', 'Seed Client Gamma']
        clients = []
        for name in key_names:
            client, created = ApiKey.objects.get_or_create(
                name=name,
                defaults={'key_hash': ApiKey.hash_key(f'seed-static-key-{name}')},
            )
            if not created:
                pass
            clients.append(client)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created ApiKey: {name}'))
            else:
                self.stdout.write(f'ApiKey already exists: {name}')

        sample_notes = [
            ('Welcome Note', 'This is your first note.', Note.STATUS_ACTIVE),
            ('Shopping List', 'Milk, eggs, bread.', Note.STATUS_ACTIVE),
            ('Old Draft', 'An archived draft note.', Note.STATUS_ARCHIVED),
            ('Meeting Notes', 'Discuss Q3 roadmap.', Note.STATUS_ACTIVE),
            ('Ideas', 'Brainstorm for next sprint.', Note.STATUS_ACTIVE),
        ]

        for i, (title, content, note_status) in enumerate(sample_notes):
            owner = clients[i % len(clients)]
            note, created = Note.objects.get_or_create(
                title=title,
                owner=owner,
                defaults={'content': content, 'status': note_status},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Note: {title}'))
            else:
                self.stdout.write(f'Note already exists: {title}')

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
