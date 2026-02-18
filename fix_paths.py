import os

root_dir = "scenarios"
old_line = 'ASSET_DIR = "../../assets"'
new_line = 'ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets")'

count = 0
for dp, dn, filenames in os.walk(root_dir):
    for f in filenames:
        if f.endswith('.py'):
            filepath = os.path.join(dp, f)
            with open(filepath, 'r') as file:
                content = file.read()
            
            if old_line in content:
                new_content = content.replace(old_line, new_line)
                with open(filepath, 'w') as file:
                    file.write(new_content)
                print(f"Fixed: {f}")
                count += 1

print(f"Total fixed: {count}")
