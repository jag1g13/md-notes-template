.DEFAULT_GOAL := edit

# Defauly to today's date
DAY := $(shell date -I)
DAY_NOTES := days/$(DAY).md

$(DAY_NOTES):
	cat template.md | awk --assign date=$(DAY) '{ gsub(/<date>/, date) } { print }' > $(DAY_NOTES)

.PHONY: edit
edit: $(DAY_NOTES)
	vim $(DAY_NOTES)

.PHONY: push
push:
	git add $(DAY_NOTES)
	git commit -S -m "$(DAY)"
	git push

