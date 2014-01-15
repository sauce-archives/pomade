import time
import re
from selenium import selenium


class implicitWaitSelenium(selenium):
    """
    Extending the regular selenium class to add implicit waits
    """

    def __init__(self, *args):
        self.implicit_wait = 30
        super(implicitWaitSelenium, self).__init__(*args)

    def do_command(self, verb, args, implicit_wait=None):
        if implicit_wait is None:
            implicit_wait = self.implicit_wait

        try:
            return super(implicitWaitSelenium, self).do_command(verb, args)
        except Exception, e:
            if (re.match("ERROR: Element .* not found", str(e))
                and implicit_wait > 0):
                time.sleep(1)
                return self.do_command(verb, args, implicit_wait - 1)
            raise


class FlexSelenium(implicitWaitSelenium):
    """
    Extending the regular selenium class to add support for flex commands
    """

    #second extension client test
    def test_working_extension(self, text):
        self.do_command("testWorkingExtension", [text])

    def flex_click(self, locator, flashLoc):
        """
        Clicks the specified display object (flashLoc), within the specified flex/flash movie (locator)
        'locator' is an element locator
        """
        self.do_command("flexClick", [locator, flashLoc])

    def flex_double_click(self, locator, flashLoc):
        """
        Double clicks the specified display object (flashLoc), within the specified flex/flash movie (locator)
        'locator' is an element locator
        """
        self.do_command("flexDoubleClick", [locator, flashLoc])

    def flex_select(self, locator, options):
        """
        Select 'options:[val|label]' from display object 'options:flexlocator' found by the locator
        'locator' is an element locator
        """
        self.do_command("flexSelect", [locator, options])

    def flex_type(self, locator, options):
        """
        Type 'options:flexlocator' into the display object 'options:opt+locator(chain,id,name)' found by the locator
        'locator' is an element locator
        """
        self.do_command("flexType", [locator, options])

    def wait_for_flex_ready(self, locator, timeout):
        self.do_command("waitForFlexReady", [locator, timeout])

    def wait_for_flex_object(self, locator, options):
        self.do_command("waitForFlexObject", [locator, options])

    def flex_drag_drop_elem_to_elem(self, locator, options):
        """
        Type 'options:text' into the display object 'options:flexlocator' found by the locator
        'locator' is an element locator
        """
        self.do_command("flexDragDropElemToElem", [locator, options])

    def flex_drag_drop_to_coords(self, locator, options):
        """
        Drag a display object 'options:flexlocator' to the coordinates (x,y)
        'locator' is an element locator
        """
        self.do_command("flexDragDropToCoords", [locator, options])

    def flex_assert_display_object(self, locator, options):
        """
        Assert a display object 'options:flexlocator' exists in the Flex/Flash movie found by locator
        'locator' is an element locator
        """
        self.do_command("flexAssertDisplayObject", [locator, options])

    def flex_assert_text(self, locator, options):
        """
        Assert a display object 'options:flexlocator' has equal contents to string 'options:validator'  in the Flex/Flash movie found by locator
        'locator' is an element locator
        """
        self.do_command("flexAssertText", [locator, options])

    def flex_assert_text_in(self, locator, options):
        """
        Assert a display object 'options:flexlocator' contains the string 'options:validator'  in the Flex/Flash movie found by locator
        'locator' is an element locator
        """
        self.do_command("flexAssertText", [locator, options])

    def flex_assert_property(self, locator, options):
        """
        Assert a display object 'options:flexlocator' contains the property and value defined by 'options:validator (property|value)'  in the Flex/Flash movie found by locator
        'locator' is an element locator
        """
        self.do_command("flexAssertProperty", [locator, options])
