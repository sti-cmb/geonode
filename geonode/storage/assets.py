from geonode.base.models import Link


class AssetManager:

    def create(self, asset_class, **kwargs):
        """
        Create an asset
        """
        asset = asset_class(**kwargs)
        asset.save()
        return asset.get_real_instance()

    def assign(self, asset, resource):
        """
        Assign an existing asset to an existing resource
        By creating the 'original' link.
        Return the LINK created
        """
        # creating the association between asset and Link
        # lets check if a original link exists
        return self._generate_link(asset, resource)

    def _generate_link(self, asset, resource=None):
        """
        Create the 'original' link for the asset
        If resource is None, the link is created without assign it to any resource.
        If an original link is already present for the resource, we assing the
        asset to it
        """
        if resource is None:
            Link.objects.create(resource=None, asset=asset, link_type="original", name="Original", url=None)
        else:
            link = resource.link_set.filter(link_type="original").first()
            if link:
                # if exists, we can assign the asset to the link
                link.asset = asset
                link.save()
            else:
                # otherwise we create the link with the assigned asset
                Link.objects.create(
                    resource=resource.get_real_instance(),
                    asset=asset,
                    link_type="original",
                    name="Original",
                    url=resource.get_real_instance().download_url,
                )


asset_manager = AssetManager()
