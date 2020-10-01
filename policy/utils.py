#!/usr/bin/env python3
# -*- coding: utf-8 -*-   

def timeStr():
    t = time.strftime(str("%Y-%m-%d %H:%M:%S"), time.localtime())
    s = '[%s]' % t
    return s