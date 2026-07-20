from eralchemy import render_er

db_url = 'sqlite:///parking_system.db'

output_file = 'er_diagram.png'

render_er(db_url, output_file)
print(f"ER diagram saved as {output_file}")
