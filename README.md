# EPICSRelay

## What is it?

This is an EPICS relay server using [pcaspy](https://github.com/paulscherrerinstitute/pcaspy). You can send data to a made up variable name fitting the naming rules (prefix & dtype-suffix) and an EPICS-PV will then be created on the fly for other clients to read from.

## Why?

I build this to have a fast solution for some specific cases:

1. You have a script running doing *something* repeatedly and just need the result value as an epics variable to process or archive or something.
2. You want to "publish" a single monitoring value from some sensor and building a server for it would be overkill.
3. Threading issues make building a server annoying sometimes.

Having this server running on some computer in your network allows you to just think of a name for your variable, use pyepics to send the value to the relay server even though it did not exist before and you can use the value in other epics-enabled software *immediately*.

## How to use:

The epics server starts with an empty pv list. New pvs can be created during run-time by putting a value to the server using the correct syntax:

```
<prefix>:<name>_<dtype><count>
```

e.g.
```python
epics.put("5trap:relay:cupsofcoffeetoday_i1", 2)
epics.put("5trap:relay:temperature_lab_f1", 21.2)
epics.put("5trap:relay:fit_results_f4", [23.0, 0.1, 3231.123, 1e-4])
epics.put("5trap:relay:pressure_log_F100", 1e-4) # this is a buffer of length 100. Values put, will be appended right.
epics.put("5trap:relay:cmdline_output_c10000", "The sun is shining, dont you want to go outside?")
```

The prefix is the server identifier, the name is an arbitray name for you to choose to describe the variable. dtype defines the value type (**f**loat, **i**nt, **c**har, **U**pper case letters for a buffer) and count gives the number of elements in this PVs array.

## Authors

* **Menno Door** - *Initial work* - [door at mpi-k.de](mailto:door@mpi-k.de)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
