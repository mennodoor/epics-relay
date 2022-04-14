# EPICSRelay

## Why?

I build this to have a **super fast** solution for the following cases:

1. I have a script running doing *something* repeatedly and I need just the result value as an epics variable to process or archive in another service.
2. I have a single monitoring value from some sensor and I am to lazy to build a server for that.
3. The needed server for a service or device only needs read-only values and still for what reason so ever I would need a bunch of complicated threading stuff and thread locking which I want to avoid.

Having this server running on some computer in your network allows you to just think of a clever name for your variable, use pyepics to send the value to the relay server using that clever name even though it did not exist before and you can use the value in other epics-enabled software *immediately*.

## How:

The epics server starts with an empty pv list. New pvs can be created during run-time by putting a value to the server using the correct syntax:

```
<prefix>:<name>_<dtype><count>
```

e.g.
```python
epics.put("5trap:relay:cupsofcoffeetoday_i1", 2)
epics.put("5trap:relay:temperature_lab_f1", 21.2)
epics.put("5trap:relay:fit_results_f4", [23.0, 0.1, 3231.123, 1e-4])
epics.put("5trap:relay:cmdline_output_c10000", "The sun is shining, dont you want to go outside?")
```

The prefix is the server identifier, the name is an arbitray name for you to choose to describe the variable. dtype defines the value type (**f**loat, **i**nt, **c**har) and count gives the number of elements in this PVs array.

## Authors

* **Menno Door** - *Initial work* - [door at mpi-hd.mpg.de](mailto:door@mpi-hd.mpg.de)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details