# EOS Event Handler

## Summary
The EOS Event Handler studio configures EOS event handlers for device sets. It supports all six EOS trigger types with comprehensive options for delay, timeout, threshold, repeat interval, and asynchronous execution.

## Features
- **All 6 Trigger Types**: on-boot, on-startup-config, on-logging, on-intf, on-counters, on-custom-condition
- **Collection-Based**: Define multiple event handlers per device set
- **Tag-Based Assignment**: Assign handler sets to groups of devices via tag queries
- **Advanced Settings**: Timeout (with optional terminate), threshold windows, repeat intervals, and asynchronous mode
- **Input Validation**: Validates required fields per trigger type (e.g. interface name for on-intf, condition expression for on-counters)

## Configuration

### Event Handler Fields

| Field | Description |
|-------|-------------|
| Handler Name | Unique name for the event handler |
| Trigger Type | One of: on-boot, on-startup-config, on-logging, on-intf, on-counters, on-custom-condition |
| Action Command | Bash command or script to run when triggered |
| Delay (seconds) | Delay between event and action (EOS default: 20s) |
| Disable Trigger on Config | Prevent action from running on config application (EOS 4.26.0F+) |

### Trigger-Specific Settings

#### on-logging
| Field | Description |
|-------|-------------|
| Syslog Regex | Regex to match against syslog messages |
| Poll Interval | How often to poll for the logging event |

#### on-intf
| Field | Description |
|-------|-------------|
| Interface Name or Range | e.g. Ethernet1, Ethernet1-36, Port-Channel1 |
| Interface Trigger On | operstatus, ip, or operstatus ip |

#### on-counters
| Field | Description |
|-------|-------------|
| Condition Expression | Counter condition using Python-style operators |
| Poll Interval | How often to evaluate the counter condition |

#### on-custom-condition (EOS 4.33.0F+)
| Field | Description |
|-------|-------------|
| Condition Script | Multi-line bash/python script for the custom condition |
| Poll Interval | How often to run the condition script |

### Advanced Settings

| Field | Description |
|-------|-------------|
| Timeout (seconds) | Maximum action duration (minimum 10s) |
| Terminate on Timeout | Kill the action if it exceeds timeout (EOS 4.33.1F+) |
| Asynchronous | Run action immediately instead of queuing |
| Threshold Window (seconds) | Sliding time window for threshold |
| Threshold Count | Events required within window to trigger |
| Repeat Interval (seconds) | Time window to limit action triggers |
| Repeat Count | Maximum triggers within repeat interval |

## Example Output

### on-startup-config (Config Versioning)
```
event-handler config-versioning
   trigger on-startup-config
   action bash FN=/mnt/flash/startup-config; LFN="`ls -1 $FN.*-* | tail -n 1`"; if [ -z "$LFN" -o -n "`diff -I 'last modified' $FN $LFN`" ]; then cp $FN $FN.`date +%Y%m%d-%H%M%S`; ls -1r $FN.*-* | tail -n +11 | xargs -I % rm %; fi
   delay 0
!
```

### on-logging (BGP Monitor with Threshold)
```
event-handler monitor-bgp
   trigger on-logging
         regex BGP
   action bash /mnt/flash/bgp-monitor.sh
   delay 10
   threshold 300 count 3
!
```

## Notes
- The `on-custom-condition` trigger type requires EOS 4.33.0F or later
- The `terminate` timeout option requires EOS 4.33.1F or later
- The `trigger on-config disabled` option requires EOS 4.26.0F or later
- Use caution with `asynchronous` mode as it disables the built-in queuing mechanism
