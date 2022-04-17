# EPICS Relay

## About

This is an [EPICS](https://epics-controls.org/) relay server written in python using the [pcaspy](https://github.com/paulscherrerinstitute/pcaspy) library. You can send data using an EPICS client, e.g. [pyepics](https://github.com/pyepics/pyepics), to a not yet existing process variable (PV) which fits the naming rules (prefix & dtype-suffix). A PV will then be created on the fly for other clients to read from. These PVs do not look any different than standard pcaspy PVs, so things like camonitor will work as normal, but the PV has to exist prior to a camonitor initialization.

There is no implementation for setting limits, units or other *higher order* PV-attributes ...yet. Only type (int, float, char) and count. And, because I needed it, a right appending buffer.

## Why?

EPICS based control systems don't use relays or brokers, its a network of servers presenting interfaces to devices or services and the underlying EPICS protocols allow clients to autoconnect to servers based on a process variable naming scheme and network broadcasts to find each other. So why would you need a relay? It's just a really easy way to publish variables from non-server scripts as PVs without building a server around them. That can be results of some online-analysis scripts, monitoring values from sensors or STDERR outputs from anywhere. Basically every device that doesn't need any input (doesn't need to be written to) can instead of building a server also use the relay. 

## How to use:

The relay server starts with an empty PV list. New PVs can be created during run-time by putting a value to the server using the correct syntax:

```
<prefix>:<name>_<dtype><count>
```

e.g.
```python
epics.put("5trap:relay:cupsofcoffeetoday_i1", 2)
epics.put("5trap:relay:temperature_lab_f1", 21.2)
epics.put("5trap:relay:fit_results_f4", [23.0, 0.1, 3231.123, 1e-4])
epics.put("5trap:relay:pressure_log_F100", 1e-4) # this is a buffer of length 100. Values put will be appended right.
epics.put("5trap:relay:cmdline_output_c10000", "The sun is shining, go outside!")
```

The prefix is the server identifier, the name is an arbitray name for you to choose to describe the variable. dtype defines the value type (**f**loat, **i**nt, **c**har, **U**pper case letters for a buffer) and count gives the number of elements in this PVs array.

## ToDo

1. Change the way the server class accesses the driver. Its using the global variable defined in if name==main and thats just not pretty.
2. Add some method to adjust units, alarm limits and other PV attributes.
3. Autosave current PV names (and values?) to recreate the PVs on server restart. That would help with camonitoring startups after system failures.

## Authors

* **Menno Door** - *Initial work* - [door at mpi-k.de](mailto:door@mpi-k.de)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
