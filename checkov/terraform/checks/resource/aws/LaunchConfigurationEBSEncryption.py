from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LaunchConfigurationEBSEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Launch configuration or instance Elastic Blocks Store" \
               " is securely encrypted"
        id = "CKV_AWS_8"
        supported_resources = ['aws_launch_configuration', 'aws_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "*_block_device/[0]/encrypted"

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at launch configuration:
            https://www.terraform.io/docs/providers/aws/r/launch_configuration.html or
            https://www.terraform.io/docs/providers/aws/d/instance.html
        :param conf: aws_launch_configuration configuration
        :return: <CheckResult>
        """
        # for key in conf.keys():
        #     # If present, the encrypted flag will be determined by the snapshot
        #     # Note: checkov does not know if snapshot is encrypted, so we default to PASSED

        root = conf.get('root_block_device')
        if not root:
            # Issue 496 - TF will create unencrypted EBS root by default if whole root_block_device block is omitted.
            return CheckResult.FAILED
        blocks = conf.get('ebs_block_device') or []

        allblocks = root + blocks

        if not allblocks:
            return CheckResult.Unknown

        for block in allblocks:
            if not block.get("encrypted") == [True]:
                if not block.get("snapshot_id"):
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = LaunchConfigurationEBSEncryption()
