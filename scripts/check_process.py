#-------------------------------------------------------------------------------
#
# The MIT License (MIT)
#
# Copyright (c) 2015 William De Freitas
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#-------------------------------------------------------------------------------

#!/usr/bin/env python

'''Checks processes'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import subprocess

# Third party modules


# Application modules



#===============================================================================
# Check script is running
#===============================================================================
def is_running(script_name):
    try:
        cmd1 = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
        cmd2 = subprocess.Popen(['grep', '-v', 'grep'], stdin=cmd1.stdout, 
                                stdout=subprocess.PIPE)
        cmd3 = subprocess.Popen(['grep', '-v', str(os.getpid())], stdin=cmd2.stdout, 
                                stdout=subprocess.PIPE)
        cmd4 = subprocess.Popen(['grep', '-v', str(os.getppid())], stdin=cmd3.stdout, 
                                stdout=subprocess.PIPE)
        cmd5 = subprocess.Popen(['grep', script_name], stdin=cmd4.stdout, 
                                stdout=subprocess.PIPE)
        return cmd5.communicate()[0] 

    except Exception, e:
        return e