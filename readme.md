# A Solution to get timetable automatically

This is designed at first to get excel timetable from http://my.cqu.edu.cn/enroll/
but failed at last because of js Ajax loading of specific page. I tried every method I can but gave up at last.
</br>
So this solution maybe design for getting token for logging in process as we have known that all requests need this
token.

# Usage

Refer to `main` function of [main.py](main.py) as a demo, and docstring of `cm_http` class.

# To List

- [x] get token
- [x] get json format timetable
- [ ] parsing timetable.json translate it to `xlsx` format for example
- [ ] using in [cqu_timetable_new](https://github.com/weearc/cqu_timetable_new)

Although I'd like to use these scripts on desktop, more people seem to get an automatically one.
</br>
Another reason why I have to build this is that I hate the new `wecqu` under the `Student Union of CQU`. I'd like to use
AGPL to force them ether opensource of their code or make another one without my function.

# License
AGPL 3.0
