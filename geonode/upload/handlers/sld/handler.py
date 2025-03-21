#########################################################################
#
# Copyright (C) 2024 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
import logging

from geonode.resource.manager import resource_manager
from geonode.upload.handlers.common.metadata import MetadataFileHandler
from geonode.upload.handlers.sld.exceptions import InvalidSldException
from owslib.etree import etree as dlxml
from geonode.upload.utils import ImporterRequestAction as ira

logger = logging.getLogger("importer")


class SLDFileHandler(MetadataFileHandler):
    """
    Handler to import SLD files into GeoNode data db
    It must provide the task_lists required to comple the upload
    """

    TASKS = {
        ira.RESOURCE_STYLE_UPLOAD.value: ("start_import", "geonode.upload.import_resource"),
        ira.ROLLBACK.value: (
            "start_rollback",
            "geonode.upload.rollback",
        ),
    }

    @property
    def supported_file_extension_config(self):
        return {
            "id": "sld",
            "formats": [
                {
                    "label": "Styled Layer Descriptor 1.0, 1.1 (SLD)",
                    "required_ext": ["sld"],
                }
            ],
            "actions": list(self.TASKS.keys()),
            "type": "metadata",
        }

    @staticmethod
    def can_handle(_data) -> bool:
        """
        This endpoint will return True or False if with the info provided
        the handler is able to handle the file or not
        """
        base = _data.get("base_file")
        if not base:
            return False
        return (base.endswith(".sld") if isinstance(base, str) else base.name.endswith(".sld")) and _data.get(
            "action", None
        ) == ira.RESOURCE_STYLE_UPLOAD.value

    @staticmethod
    def is_valid(files, user, **kwargs):
        """
        Define basic validation steps
        """
        # calling base validation checks
        try:
            with open(files.get("base_file")) as _xml:
                dlxml.fromstring(_xml.read().encode())
        except Exception as err:
            raise InvalidSldException(f"Uploaded document is not SLD or is invalid: {str(err)}")
        return True

    def handle_metadata_resource(self, _exec, dataset, original_handler):
        if original_handler.can_handle_sld_file:
            original_handler.handle_sld_file(dataset, _exec)
        else:
            _path = _exec.input_params.get("files", {}).get("sld_file", _exec.input_params.get("base_file", {}))
            resource_manager.exec(
                "set_style",
                None,
                instance=dataset,
                sld_file=_exec.input_params.get("files", {}).get("sld_file", ""),
                sld_uploaded=True if _path else False,
                vals={"dirty_state": True},
            )
