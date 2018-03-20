Qth National Rail
=================

Add UK rail train information from the [National Rail Enquiries 'Darwin' data
feed](http://www.nationalrail.co.uk/100296.aspx) to Qth.

Example usage:

    $ qth_darksky XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX spt man --path=transport/rail/spt

The first argument is an API key for the Darwin 'Lite' web service. The second
and third arguments are starting and destination station three-letter-codes.
The following Qth properties are created:

**`[path]`**

A simplified timetable. A list of strings containing the departure times of
non-cancelled services in the form `<scheduled time> (<estimated time>)`.

**`[path]/detailed`**

The full JSON-serialised response of the `GetDepBoardWithDetails` command from
the [OpenLDBWS API](http://lite.realtime.nationalrail.co.uk/openldbws/).
