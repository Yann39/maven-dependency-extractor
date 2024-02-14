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
        dependencies_versions: A dictionary representing dependencies along with their versions (property name associating a tuple of last version and minimum desired version)
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
    Get specified properties name and value from the specified XML string

    Args:
        xml_string: The XML string to search in
        properties: The properties to search for (list of string)

    Returns:
        A list of tuples (property name and value) representing repository properties
    """
    root = xml.etree.ElementTree.fromstring(xml_string)
    ns = {'pom': 'http://maven.apache.org/POM/4.0.0'}
    values = [("artifactId", get_tag_value(root, ns, "artifactId")), ("version", get_tag_value(root, ns, "version"))]
    for prop in properties:
        values.append((prop, get_property_tag_value(root, ns, prop)))
    return values


def get_versions_table(repositories, properties, credentials):
    """
    Build a table of all properties for specified repositories

    Args:
        repositories: The repositories to check (list of string)
        properties: The properties to search for (list of string)
        credentials: The credentials to connect to repositories (login/password tuple)

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
        dependencies_versions: A dictionary representing dependencies along with their versions (property name associating a tuple of last version and minimum desired version)

    Returns:
        A String representing the HTML table
    """
    table_header = "<tr>\n"
    for col in repositories_properties[0]:
        table_header = table_header + '<th scope="col">{colName}</th>\n'.format(colName=col[0])
    table_header = table_header + "</tr>\n"

    table_body = ""
    for line in repositories_properties:
        table_body = table_body + "<tr>\n"
        for col in line:
            if col[0] == "artifactId":
                table_body = table_body + '<th scope="row">{version}</th>\n'.format(version=col[1])
            elif col[0] == "version":
                table_body = table_body + '<td>{version}</td>\n'.format(version=col[1])
            else:
                table_body = table_body + '<td><span class="badge badge-{color}">{version}</span></td>\n'.format(
                    color=get_version_badge_color(dependencies_versions, col), version=col[1])
        table_body = table_body + "</tr>\n"

    html_template = """
        <!doctype html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
                <title>My projects</title>
            </head>
            <body style="background-color:#ccc">
                <div class="container">
                    <div class="row">
                        <div class="col">
                            <h1>Maven project dependency versions</h1>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col">
                            <div class="table-responsive">
                                <table class="table table-bordered table-hover table-striped table-dark">
                                    <thead>
                                        {tableHeader}
                                    </thead>
                                    <tbody>
                                        {tableBody}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
    """.format(tableBody=table_body, tableHeader=table_header)
    return html_template


# Credentials
authentication_data = ("login", "password")

# List of dependencies to consider, with their latest version and the minimum desired version
dependencies_versions_list = {
    "java.version": ("12", "8"),
    "zk.version": ("9.0.0", "8.6.0"),
    "spring.boot.version": ("2.2.2.RELEASE", "2.0.0.RELEASE")
}

# List of repositories to check
repositories_list = [
    "https://github.com/api/v3/repos/my-org/my-project1/contents/pom.xml",
    "https://github.com/api/v3/repos/my-org/my-awesome-project/contents/pom.xml",
    "https://github.com/api/v3/repos/my-other-org/my-project-2/contents/pom.xml",
    "https://github.com/api/v3/repos/my-other-org/just-another-project/contents/pom.xml",
    "https://github.com/api/v3/repos/my-other-org/hate-this-project/contents/pom.xml",
    "https://github.com/api/v3/repos/my-other-org/project-3/contents/pom.xml",
    "https://github.com/api/v3/repos/another-org/another-funny-projet/contents/pom.xml",
]

all_properties = get_versions_table(repositories_list, dependencies_versions_list.keys(), authentication_data)
html_table = generate_html_table(all_properties, dependencies_versions_list)

# write content in an HTML file
output_file = open("versions.html", "w")
output_file.write(html_table)
output_file.close()
