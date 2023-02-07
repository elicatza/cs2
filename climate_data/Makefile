PROGRAMNAME=climate_data
PROGRAM= $(PROGRAMNAME).py
PREFIX=/usr/local
INSTALL_PATH=$(PREFIX)/bin


install:
	chmod 755 $(PROGRAM)
	mkdir -p $(INSTALL_PATH)
	cp $(PROGRAM) $(INSTALL_PATH)/$(PROGRAM)

	mkdir -p /var/local/$(PROGRAMNAME)
	cp $(PROGRAMNAME).service /etc/systemd/system
	cp $(PROGRAMNAME).timer /etc/systemd/system

	mkdir -p /var/local/$(PROGRAMNAME)

# remove system files
uninstall:
	rm $(INSTALL_PATH)/$(PROGRAM)
	rm /etc/systemd/system/$(PROGRAMNAME).service
	rm /etc/systemd/system/$(PROGRAMNAME).timer

# Remove stored data
clean:
	rm -r /var/local/$(PROGRAMNAME)

.PHONY: install uninstall clean
