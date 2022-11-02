It is possible to access Reddit public API by appending `.json` to the URL pointing to a page, e.g. https://www.reddit.com/r/popular.json

Write a command that would compare current JSON data with JSON data during its previous run, and print out:

- New posts
- Posts that are no longer within the top 75 posts
- Posts whose vote count changed, with the amount of change

(Additionally create an archiving system for past comparisons)
