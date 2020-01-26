# Maven multi-projects dependencies extractor

Simple Python program that parse multiple remote Maven projects (POM files) to build a summary table of dependency versions.

## Technologies

- Python 3.4.4
- Bootstrap 4.4.1

## Prerequisites

1. Modify `repositories_list variable` variable to include your repositories
2. Modify `dependencies_versions_list` variable to include your artifact ids and versions
3. Modify `authentication_data` variable to include your credentials to connect to your repositories

POM files must be valid POM format and contains the namespace `http://maven.apache.org/POM/4.0.0`.

You must have `<artifactId>` and `<version>` nodes under your `<project>` node.

All dependencies versions should be inside a `<properties>` node.

Example :

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <artifactId>my-project</artifactId>
    <version>2.1.1</version>

    <properties>
        <spring.boot.version>2.2.2.RELEASE</spring.boot.version>
        <zk.version>9.0.0</zk.version>
        <commons-lang3.version>3.9</commons-lang3.version>
        ...
    </properties>

    ...

</project>
```

## Usage

Simply run the `read_pom.py` file.

## Output

It generates an HTML file in the project directory named `versions.html`.

Here is an example output :

![Login page screenshot](output.png "Generated HTML file")

## Licence

[General Public License (GPL) v3](https://www.gnu.org/licenses/gpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.
    
You should have received a copy of the GNU General Public License along with this program.  If not,
see <http://www.gnu.org/licenses/>.