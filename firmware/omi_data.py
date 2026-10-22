# Omi-Version: eigene, ganz einfache Weboberflaeche (web/omi statt web/static)
Import("env")
import os
env.Replace(PROJECT_DATA_DIR=os.path.normpath(os.path.join(env.subst("$PROJECT_DIR"), "..", "web", "omi")))
