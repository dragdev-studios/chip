# exit codes
These are exit codes used in interactive parts of the bot, before it starts.

**Any non-zero exit code means something errored!**

## Table
| code | description |
| ---- | ----------- |
| 0    | No issues.  |
| 1    | Fatal exception |
| 2    | User Input derived error (e.g. got wrong input type) |
| 3    | Reserved. |
| 4    | Configuration error (check config.json) |
| 9    | Generic error (usually comes with an error message)
