# Python Concepts

The Airbyte CDK makes use of various not-so-obvious Python concepts. You might want to revisit these concepts as you implement your connector:

## Abstract Classes [ABCs \(AbstractBaseClasses\)](https://docs.python.org/3/library/abc.html) and [abstractmethods](https://docs.python.org/3/library/abc.html#abc.abstractmethod)

You'll want a strong understanding of these as the central API concepts require extending and using them.

## [Keyword Arguments](https://realpython.com/python-kwargs-and-args/).

You'll often see this referred to as `**kwargs` in the code.

## [Properties](https://www.freecodecamp.org/news/python-property-decorator/)

Note that there are two ways of defining properties: statically and dynamically.

### Statically

```text
class Employee(ABC):
    @property
    @abstractmethod
    def job_title():
        """ returns this employee's job title"""

class Pilot(Employee):
    job_title = "pilot"
```

Notice how statically defining properties in this manner looks the same as defining variables. You can then reference this property as follows:

```text
pilot = Pilot()
print(pilot.job_title) # pilot
```

### Dynamically

You can also run arbitrary code to get the value of a property. For example:

```text
class Employee(ABC):
    @property
    @abstractmethod
    def job_title():
        """ returns this employee's job title"""

class Pilot(Employee):
    def job_title():
        # You can run any arbitrary code and return its result
        return "pilot"
```

## [Generators](https://wiki.python.org/moin/Generators)

Generators are basically iterators over arbitrary source data. They are handy because their syntax is extremely concise and feel just like any other list or collection when working with them in code.

If you see `yield` anywhere in the code -- that's a generator at work.

