# Notes

This repo is for me to keep notes of my daily work.
A Markdown file should be created every day with a brief summary of what was happening.
Each day's notes should have a yaml header with the date and a rough breakdown of time spent on each project.

This is all handled using a Markdown template and a Makefile with some AWK.


## Usage

Edit today's notes - create from template if missing:

```
make edit
```

Publish today's notes to git repo:

```
make push
```

Edit notes of a specific day - create from template if missing:

```
make edit DAY="2021-01-01"
```
