import unittest

from creAI.cli import CommandlineInterface, command
from creAI.exceptions import *

class TestCLI(unittest.TestCase):
    def test_init(self):
        class App(CommandlineInterface):
            """Something

            Other thing.
            """
            def __init__(self):
                super(App, self).__init__()

            @command
            def foo(self, a, b):
                """Foo

                Foooooooo.

                Args:
                    a (int): Foo arg 1.
                    b (int): Foo arg 2.
                """
                pass

        App()
        
        class App2(CommandlineInterface):
            """Something

            Other thing.
            """
            def __init__(self):
                super(App2, self).__init__()

            @command
            def foo(self, a, b):
                """Foo

                Foooooooo.

                """
                pass

        App2()

        with self.assertRaises(MissingCommandDocstring):
            class AppMissingDocstring(CommandlineInterface):
                """Something

                Other thing.
                """
                def __init__(self):
                    super(AppMissingDocstring, self).__init__()

                @command
                def foo(self, a, b):
                    pass

            AppMissingDocstring()

        with self.assertRaises(MissingAppDocstring):
            class AppMissingDocstring2(CommandlineInterface):
                def __init__(self):
                    super(AppMissingDocstring2, self).__init__()

                @command
                def foo(self, a, b):
                    """Foo

                    Foooooooo.

                    Args:
                        a (int): Foo arg 1.
                        b (int): Foo arg 2.
                    """
                    pass

            AppMissingDocstring2()


if __name__ == '__main__':
    unittest.main()