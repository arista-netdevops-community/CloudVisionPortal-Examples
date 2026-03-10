# EOS Aliases

## Summary
The EOS Aliases studio configures EOS command aliases for device sets. Aliases provide shorthand commands that expand to full EOS CLI commands, improving operational efficiency.

## Features
- **Collection-Based**: Define any number of aliases, each with a name and command
- **Tag-Based Assignment**: Assign alias sets to groups of devices via tag queries
- **Input Validation**: Alias names are validated against the pattern `^[a-zA-Z][a-zA-Z0-9_-]*$`
- **Positional Arguments**: Alias commands support `%1`, `%2`, etc. for positional argument substitution

## Configuration

### Alias Device Sets
Assign a set of aliases to a group of devices. Each alias entry requires:

| Field | Description |
|-------|-------------|
| Alias Name | The shorthand name (e.g. `snz`). Must start with a letter, containing only letters, numbers, underscores, or hyphens |
| Alias Command | The full command the alias expands to (e.g. `show interface counter \| nz`) |

## Example Output
```
alias conint show interface | include connected
alias dump bash tcpdump -i %1 -s 0 -U -w /mnt/flash/%2
alias findmac bash /mnt/flash/findmac.sh %1
alias routeage bash /mnt/flash/routeage.py %1
alias scp bash scp %1 %2
alias senz show interface counter error | nz
alias shinz show interface counter | nz
alias shmc show int | awk '/^[A-Z]/ { intf = $1 } /^\s+Member/ { print intf, $0 }'
alias shvxaddr show vxlan address-table
alias snz show interface counter | nz
alias spd show port-channel %1 detail all
alias sqnz show interface counter queue | nz
alias srnz show interface counter rate | nz
```

## Notes
- Aliases with empty names or commands are silently skipped
- The studio uses `MULTI_DEVICE_TAG` resolver mode so a single alias set can be applied to many devices at once
