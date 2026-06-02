import urllib.request
import urllib.parse
import re
import time

exercises = [
    'frontraise', 'barbellrow', 'situp', 'tricepextension', 'latpulldown', 'pushup', 
    'inclinepushup', 'widepushup', 'diamondpushup', 'squat', 'goblet', 'jumpsquat', 
    'lunge', 'bulgariansplit', 'deadlift', 'pullup', 'shoulderpress', 'lateralraise', 
    'curl', 'dips', 'plank', 'mountainclimbers', 'russiantwist', 'legraises', 
    'run', 'jumpingjacks', 'burpee', 'calfraise'
]

mapping = {}

# Simple fallback dictionary in case of rate limits
fallback = {
    'pushup': 'IODxDxX7oi4',
    'squat': 'MVMNK0HiVQA',
    'plank': 'ASdvN_XEl_c',
    'run': '54OOGwH1T-w'
}

for ex in exercises:
    query = urllib.parse.quote(f"how to {ex} exercise perfect form")
    url = f"https://www.youtube.com/results?search_query={query}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req).read().decode('utf-8')
        match = re.search(r'"videoId":"(.*?)"', res)
        if match:
            vid = match.group(1)
            mapping[ex] = vid
        else:
            mapping[ex] = fallback.get(ex, 'IODxDxX7oi4')
    except Exception as e:
        mapping[ex] = fallback.get(ex, 'IODxDxX7oi4')
    
    time.sleep(0.5)

map_str = "{\n"
for k, v in mapping.items():
    map_str += f"      '{k}': '{v}',\n"
map_str += "    }"

print("Found mapping:")
print(map_str)

html_path = r'c:\Users\Kande Sunhith\Downloads\gym-app-v3.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

replacement = """const YT_MAP = """ + map_str + """;

    const A = new Proxy({}, {
      get: function(target, prop) {
        return function(sz, label) {
          const vid = YT_MAP[prop] || 'IODxDxX7oi4';
          return `<div style="width:${sz}px;height:${Math.round(sz*1.2)}px;border-radius:16px;background:#181824;overflow:hidden;position:relative;">
                    <iframe width="100%" height="100%" 
                            src="https://www.youtube.com/embed/${vid}?autoplay=1&mute=1&loop=1&playlist=${vid}&controls=0&modestbranding=1&showinfo=0" 
                            title="Exercise Animation" frameborder="0" 
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                            allowfullscreen style="pointer-events: none;"></iframe>
                  </div>`;
        }
      }
    });

"""

# Finding indices
start_marker = "const A = new Proxy("
end_marker = "    //  EXERCISE DATABASE"
start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_html = html[:start_idx] + replacement + html[end_idx:]
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("SUCCESS: Replaced Video loader with streaming YouTube perfect-human player.")
else:
    print("ERROR: Markers not found.")
