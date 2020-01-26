# Copyright (c) 2019 by Yann39.
#
# This file is part of Maven multi-project dependencies extractor application.
#
# Maven multi-project dependencies extractor is free software: you can
# redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Maven multi-project dependencies extractor is distributed in the hope
# that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Maven multi-project dependencies extractor. If not,
# see <http://www.gnu.org/licenses/>.

import requests
import base64
import xml.etree.ElementTree
import pip
package = 'packaging'
pip.main(['install', package])
from packaging import version

def get_version_badge_color(dependencies_versions, dependency):
    """
    Get badge color for the specified dependency

    Args:
        dependencies_versions: A dictionary representing dependencies along with their versions (tuple of last version and minimum desired version)
        dependency: A tuple representing the dependency (name and current version)

    Returns:
        The badge color as string
    """
    if dependency[0] in dependencies_versions:
        if dependency[1] == "None":
            return "secondary"
        elif version.parse(dependency[1]) < version.parse(dependencies_versions[dependency[0]][1]):
            return "danger"
        elif version.parse(dependency[1]) < version.parse(dependencies_versions[dependency[0]][0]):
            return "warning"
        else:
            return "success"
    else:
        return "light"

def get_property_tag_value(xml_root, namespace, tag_name):
    """
    Get the specified tag version value from the properties in the specified XML content

    Args:
        xml_root: The XML root object
        namespace: The XML namespace associated with the property tags
        tag_name: The property tag name to search for

    Returns:
        The tag value
    """
    version_tag = xml_root.find("pom:properties", namespace).find("pom:" + tag_name, namespace)
    version_text = version_tag.text if version_tag is not None else "None"
    return version_text

def get_tag_value(xml_root, namespace, tag_name):
    """
    Get the specified tag value from the specified XML content

    Args:
        xml_root: The XML root object
        namespace: The XML namespace associated with the property tags
        tag_name: The property tag name to search for

    Returns:
        The tag value
    """
    version_tag = xml_root.find("pom:" + tag_name, namespace)
    version_text = version_tag.text if version_tag is not None else "None"
    return version_text

def get_repository_properties(xml_string, properties):
    """
    Get properties name and value from the specified XML string

    Args:
        xml_string: The XML string to search in
        properties: The list of properties to search for

    Returns:
        A dictionary representing properties along with their values
    """
    root = xml.etree.ElementTree.fromstring(xml_string)
    ns = {'pom': 'http://maven.apache.org/POM/4.0.0'}
    values = {"artifactId": get_tag_value(root, ns, "artifactId"), "version": get_tag_value(root, ns, "version")}
    for prop in properties:
        values[prop] = get_property_tag_value(root, ns, prop)
    return values

def get_versions_table(repositories, properties, credentials):
    """
    Build a table of all properties for specified repositories

    Args:
        repositories: The repositories to check
        properties: The list of properties to search for
        credentials: The credentials (login/password tuple) to connect to repositories

    Returns:
        An array of dictionaries representing the properties names and values for each repository
    """
    table = []
    for repo in repositories:
        resp = requests.get(repo, auth=credentials)
        if resp.status_code == 200:
            json_data = resp.json()
            file_content = base64.b64decode(json_data["content"])
            table.append(get_repository_properties(file_content, properties))
    return table

def generate_html_table(repositories_properties, dependencies_versions):
    """
    Build an HTML table displaying all repositories properties

    Args:
        repositories_properties: The table of all properties for all repositories
        dependencies_versions: A dictionary representing dependencies along with their versions (tuple of last version and minimum desired version)

    Returns:
        A String representing the HTML table
    """
    table_header = "<tr>"
    for col in repositories_properties[0]:
        table_header = table_header + '<th scope="col">{colName}</th>'.format(colName=col)
    table_header = table_header + "</tr>"

    table_body = ""
    for line in repositories_properties:
        table_body = table_body + "<tr>"
        for col in line:
            if col == "artifactId":
                table_body = table_body + '<th scope="row">{version}</th>'.format(version=line[col])
            elif col == "version":
                table_body = table_body + '<td>{version}</td>'.format(version=line[col])
            else:
                table_body = table_body + '<td><span class="badge badge-{color}">{version}</span></td>'.format(color=get_version_badge_color(dependencies_versions, (col, line[col])), version=line[col])
        table_body = table_body + "</tr>"

    html_template = """
        <!doctype html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
                <title>My projects</title>
            </head>
            <body>
                <table class="table table-sm">
                    <thead>
                        {tableHeader}
                    </thead>
                    <tbody>
                        {tableBody}
                    </tbody>
                </table>
            </body>
        </html>
    """.format(tableBody=table_body, tableHeader=table_header)
    return html_template

# Credentials
authentication_data = ("login", "password")

# List of dependencies to consider, with their latest version and the minimum desired version
dependencies_versions_list = {
    "zk.version": ("9.0.0", "8.6.0"),
    "spring.boot.version": ("2.2.2.RELEASE", "2.0.0.RELEASE"),
    "commons-lang3.version": ("3.9", "3.5"),
}

# List of repositories to check
repositories_list = [
    "https://github.com/api/v3/repos/my-org/project1/contents/pom.xml",
    "https://github.com/api/v3/repos/my-org/project2/contents/pom.xml",
    "https://github.com/api/v3/repos/my-other-org/project3/contents/pom.xml",
]

all_properties = get_versions_table(repositories_list, dependencies_versions_list.keys(), authentication_data)
html_table = generate_html_table(all_properties, dependencies_versions_list)

# write content in an HTML file
file = open("versions.html", "w")
file.write(html_table)
file.close()
