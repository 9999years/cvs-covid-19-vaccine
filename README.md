# CVS COVID-19 Vaccine Finder script

Scrapes the [CVS COVID-19 vaccine page][cvs-vaccine] page for information on
vaccine availabilities in a particular state.

```
$ python3.8 cvs.py ma
Status as of 2021-03-22 17:35:13.179000-04:00. Availability can change quickly based on demand.
No availabilities found; checked 145 CVS locations in Massachusetts
More information: https://www.cvs.com/immunizations/covid-19-vaccine

$ python3.8 cvs.py tx
Status as of 2021-03-22 17:35:13.179000-04:00. Availability can change quickly based on demand.
Available: LUBBOCK
Available: LUFKIN
Available: PALESTINE
Schedule an appointment now: https://www.cvs.com/vaccine/intake/store/covid-screener/covid-qns
More information: https://www.cvs.com/immunizations/covid-19-vaccine
```

[cvs-vaccine]: https://www.cvs.com/immunizations/covid-19-vaccine
