import requests, sqlite3, os, urllib
from bs4 import BeautifulSoup as bs


# CONFIGURATION
docset_name = 'Cython.docset'
output = docset_name + '/Contents/Resources/Documents/'

# create docset directory
if not os.path.exists(output): os.makedirs(output)

# add icon
icon = 'http://cython.org/logo/cython-logo-C.svg'
urllib.urlretrieve(icon, docset_name + "/icon.png")


def update_db(name, typ, path):
  
  cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
  fetched = cur.fetchone()
  if fetched is None:
      cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
      print('DB add >> name: %s, path: %s' % (name, path))
  else:
      print("record exists")


def add_urls():
 
  pages = {
    "Guide": "http://docs.cython.org/",
    "func": "http://docs.cython.org/src/reference/index.html",
      }
  # loop through each index page:
  for p in pages:
    typ = p
    # souping each page
    html = requests.get(pages[p]).text
    soup = bs(html)
    for a in soup.findAll('a'):
      name = a.text.strip()
      path = a.get('href')
      if path is not None and not path.startswith('http'):
        if p == 'Guide':
          path = 'docs.cython.org/' + path
        if p == 'func':
          path = 'docs.cython.org/src/reference/' + path
        update_db(name, typ, path)


def add_infoplist():
  name = docset_name.split('.')[0]
  info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
         "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> " \
         "<plist version=\"1.0\"> " \
         "<dict> " \
         "    <key>CFBundleIdentifier</key> " \
         "    <string>{0}</string> " \
         "    <key>CFBundleName</key> " \
         "    <string>{1}</string>" \
         "    <key>DocSetPlatformFamily</key>" \
         "    <string>{2}</string>" \
         "    <key>isDashDocset</key>" \
         "    <true/>" \
         "    <key>isJavaScriptEnabled</key>" \
         "    <true/>" \
         "    <key>dashIndexFilePath</key>" \
         "    <string>{3}</string>" \
         "</dict>" \
         "</plist>".format(name, name, name, 'docs.cython.org/' + 'index.html')
  open(docset_name + '/Contents/info.plist', 'wb').write(info)

db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
cur = db.cursor()
try:
    cur.execute('DROP TABLE searchIndex;')
except:
    pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
# start
add_urls()
add_infoplist()

# commit and close db
db.commit()
db.close()
