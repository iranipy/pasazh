import os
import operator
count = {
    'config': 0,
    'auth': 0,
    'main': 0,
    'notification': 0
}
for root, dirs, files in os.walk('api'):
    for file in files:
        if file in ['asgi.py', 'wsgi.py', 'apps.py']:
            continue
        elif file.endswith('.py'):
            if 'migrations' in root or 'irtech_api_venv' in root:
                continue
            with open(f'{root}\\{file}') as writen_code:
                writen_code.seek(0)
                lines = writen_code.readlines()
                for line in lines:
                    if line == '\n':
                        lines.remove(line)
                line_count = len(lines)
            try:
                project = root.split('\\')[1]
            except IndexError:
                continue
            count[project] += line_count

total = sum(list(count.values()))
count['most_lines'] = max(count.items(), key=operator.itemgetter(1))[0]
count['total'] = total

print(count)

input()
