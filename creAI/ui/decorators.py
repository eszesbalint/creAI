import creAI.globals
from creAI.ui.ui_elements import Dialog_Window, Paragraph, Progress_Bar, Code_Block, Button_List, Button
from creAI.ui.helper_functions import function_to_script, remove_ui_element
import traceback


def display_loading_animation(label: str):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if not creAI.globals.cli_mode:
                d_w = Dialog_Window(
                    title=label,
                    content=[
                        Paragraph(
                            text='Executing: {}'.format(function.__name__)
                        ),
                        Progress_Bar(),
                    ]
                )
                d_w.create()
                result = function(*args, **kwargs)
                d_w.destroy()
            else:
                result = function(*args, **kwargs)
            return result
        #wrapper.__name__ = function.__name__
        return wrapper
    return decorator


def display_error_message_on_error(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            if not creAI.globals.cli_mode:
                id_ = creAI.globals.gen_id()
                d_w = Dialog_Window(
                    title='Error while executing {}!'.format(
                        function.__name__),
                    content=[
                        Paragraph(text='{}: {}'.format(
                            type(e).__name__, str(e))),
                        Code_Block(code=traceback.format_exc()),
                        Button_List(
                            content=[
                                Button(
                                    text='OK',
                                    script=function_to_script(
                                        remove_ui_element,
                                        id_
                                    )
                                ),
                                Button(text='Cancel'),
                            ]
                        ),
                    ]
                )
                d_w.id = id_
                d_w.create()
            else:
                print(traceback.format_exc())
    wrapper.__name__ = function.__name__
    return wrapper
