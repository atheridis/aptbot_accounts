import os
import re
import sqlite3

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


class Expression:
    def __init__(self, name: str, list_id: int, method: str, value: str):
        self.name = name
        self.list_id = list_id
        self.method = method
        self.value = value

    def eval(self):
        conn = sqlite3.connect(os.path.join(PATH, "variables.db"))
        c = conn.cursor()

        if self.list_id:
            # TODO
            c.execute(
                """
                SELECT
                    *
                FROM
                    list_values
                INNER JOIN methods USING(type)
                WHERE
                    list_values.name = ?
                    AND list_values.id = ?
                    AND methods.name = ?
                """,
                (self.name, self.list_id, self.method),
            )
        conn.close()
        pass

    def __repr__(self) -> str:
        print(type(self.list_id))
        return f"Expression('{self.name}', '{self.list_id}', '{self.method}', '{self.value}')"


def parse(text: str):
    value = text
    reg_parse = re.compile(r"\$(\w+)\[?(\d+)?\]?\.(\w+)\((.+)?\)")

    expressions: list[Expression] = []
    while True:

        try:
            name, list_id, method, value = reg_parse.findall(value)[0]
            list_id = int(list_id)
        except IndexError:
            break
        except ValueError:
            list_id = None
        expressions.append(Expression(name, list_id, method, value))
    print(expressions)
    if 2:
        return None
    return ""


if __name__ == "__main__":
    # parse(r"$fib[12].set($fib[11].add($fib[10].value()))")
    # parse(r"$quotes[2].set(Hello, world)")
    # parse(r"")
    parse(r"wqe$quotes[].set($quotes[1].value(dw) + fw)")
