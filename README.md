# Slap it!
A simple decals addon for Blender 2.8+

Demo: https://youtu.be/zqwmFhVqjV0

## Download and installation

1. Download latest `slap_it.py` from https://github.com/artempoletsky/blender_slap_it/releases
2. In Blenders preferences install the addon from the file
3. Enable built-in Blenders addon `Import images as planes`

## Usage

1. In object mode press shift + A > Image > Images as planes. Add decal image you want to scene. 
2. In snapping settings enable snapping, Snap to `Face`, Snap with `Active`, Align Rotation to Target. Use material preview shading in the viewport. Snap image to place you want. 
3. With image selected select target object. Open context menu (W or Right Click). Press `Slap it!`.
4. Adjust appearance of the decal via shader editor. Adjust height offset of the decal via strength of the displace modifier.

The addon uses blenders knife project feature. So you can use it not only on plains but on any object that can be projected. If there are issues with the knife project, they appear in the script.

You can support me on Gumroad, if you like my work. https://gum.co/litSq

