# utils

This module is a Python version-agnositc tool belt for other projects designed to be implemented as a submodule. These tools are designed to be simple programs that provide flexible funcionality for use among various projects.

## colors
A class that converts hexadecimal strings into macros for printing to console.

## connection
A TCP connection class that allows the creation of Python servers or clients. It is designed to handle large collection of bytes and implements functionality that ensures all data has been sent/received using a handshake protocol.

## scraper
A module that creates different web bots to scrape data online. It uses an abstract class to build the foundation to create bots specifically for different websites. Currently supports:
- GitHub
- Google Images (WIP)

## sqlite_db
A module that allows basic functionality for an SQLite database. It converts common SQLite functionality into simple one-line commands for use in general projects.