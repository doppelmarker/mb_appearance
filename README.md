# mb_appearance
Small Python program to manipulate Mount &amp; Blade character appearance.

Install it with:

`pip install mb-app`

## Usage

    usage: mb-app [-h] [-v] [--verbose] [--quiet] [-l] [--show-face-codes] [-g N]
                  [-d INDEX_OR_NAME] [-b BACKUP_TO] [-s] [-r RESTORE_FROM]
                  [--wse2]

    Python util for Mount&Blade characters file manipulation.

    options:
      -h, --help                                Show this help message and exit.
      -v, --version                             Print version info.
      --verbose                                 Output verbose status messages.
      --quiet                                   Suppress all output except errors.
      -l, --list                                List all characters.
      --show-face-codes                         Show face codes when listing
                                                characters.
      -g N, --gen N                             Generate N random characters.
      -d INDEX_OR_NAME, --delete INDEX_OR_NAME  Delete a character by index or
                                                name.
      -b BACKUP_TO, --backup BACKUP_TO          Backup characters file.
      -s, --show                                Show backuped characters.
      -r RESTORE_FROM, --restore RESTORE_FROM   Restore characters file from
                                                backup.
      --wse2                                    Use WSE2 (Warband Script Enhancer
                                                2) profiles directory.

## Examples

```bash
# Backup current characters
mb-app --backup my_backup

# List available backups  
mb-app --show

# Generate 5 random characters
mb-app --gen 5

# Restore from a backup
mb-app --restore my_backup

# Delete a character by name
mb-app --delete "John Doe"

# Delete a character by index (0-based)
mb-app --delete 2

# Use WSE2 profiles directory
mb-app --wse2 --backup wse2_backup
```

## Web Face Editor (work in progress)

![Demo](https://github.com/doppelmarker/mb_appearance/blob/main/M%26B%20Face%20Editor%20MVP.gif)
