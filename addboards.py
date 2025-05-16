import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from board.models import Board


def create_boards():
    # Delete all existing boards (optional)
    Board.objects.all().delete()

    # Create new boards
    boards = [
        ("Random", "b", "Random discussions"),
        ("Political", "pol", "Political discussions"),
        ("STEM", "stem", "Science, Technology, Engineering and Math"),
        ("Art", "a", "Cool drawings :3"),
        ("Gayming", "vg", "Steam supremacy"),
        ("Outside activities", "o", "Touching grass"),
        ("Legal tips", "la", "Very very legal tips"),
        ("Motor's world", "mw", "Fuel drinkers")
    ]

    for name, code, desc in boards:
        Board.objects.create(name=name, code=code, description=desc)

    print(f"Created {len(boards)} boards!")


if __name__ == "__main__":
    create_boards()