import os

# Remove database file
if os.path.isfile('catalog.db'):
	os.remove('catalog.db')

# Import, creating database schema
from database import get_session, Category, Item

# Get database session
session = get_session()

# Add categories (game genres)
session.add(Category(name = 'Platform'))
session.add(Category(name = 'Puzzle'))
session.add(Category(name = 'Survival'))
session.add(Category(name = 'Maze'))

# Add items (games)
session.add(Item(creator = '', name='Super Mario Bros', desc='Super Mario Bros', category_id=1))
session.add(Item(creator = '', name='Portal', desc='Portal', category_id=2))
session.add(Item(creator = '', name='DayZ', desc='DayZ', category_id=3))
session.add(Item(creator = '', name='Pacman', desc='Pacman game', category_id=4))

# Commit database
session.commit()
