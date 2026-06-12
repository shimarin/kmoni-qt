PREFIX  = $(HOME)/.local
BINDIR  = $(PREFIX)/bin
APPDIR  = $(PREFIX)/share/applications
ICONDIR = $(PREFIX)/share/icons/hicolor/scalable/apps

.PHONY: install uninstall

install:
	install -Dm755 main.py $(BINDIR)/kmoni-qt
	install -Dm644 icon.svg $(ICONDIR)/kmoni-qt.svg
	install -d $(APPDIR)
	( echo '[Desktop Entry]'; \
	  echo 'Type=Application'; \
	  echo 'Name=強震モニタ'; \
	  echo 'Comment=防災科研 強震モニタ ビューア'; \
	  echo 'Exec=$(BINDIR)/kmoni-qt'; \
	  echo 'Icon=kmoni-qt'; \
	  echo 'Categories=Science;'; \
	  echo 'Terminal=false' ) > $(APPDIR)/kmoni-qt.desktop
	chmod 644 $(APPDIR)/kmoni-qt.desktop
	-gtk-update-icon-cache -f -t $(PREFIX)/share/icons/hicolor 2>/dev/null
	-update-desktop-database $(APPDIR) 2>/dev/null

uninstall:
	rm -f $(BINDIR)/kmoni-qt
	rm -f $(ICONDIR)/kmoni-qt.svg
	rm -f $(APPDIR)/kmoni-qt.desktop
	-gtk-update-icon-cache -f -t $(PREFIX)/share/icons/hicolor 2>/dev/null
	-update-desktop-database $(APPDIR) 2>/dev/null
