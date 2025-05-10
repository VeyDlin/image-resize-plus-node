from typing import Literal
from PIL import Image


from invokeai.invocation_api import (
    BaseInvocation,
    InputField,
    invocation,
    InvocationContext,
    ImageField,
    ImageOutput
)

PIL_RESAMPLING_MODES = Literal[
    "nearest",
    "box",
    "bilinear",
    "hamming",
    "bicubic",
    "lanczos",
]


PIL_RESAMPLING_MAP = {
    "nearest": Image.Resampling.NEAREST,
    "box": Image.Resampling.BOX,
    "bilinear": Image.Resampling.BILINEAR,
    "hamming": Image.Resampling.HAMMING,
    "bicubic": Image.Resampling.BICUBIC,
    "lanczos": Image.Resampling.LANCZOS,
}

RESIZE_MODES = Literal[
    "fill",
    "stretch",
    "fit",
    "center",
    "crop",
]


@invocation(
    "image_resize_plus",
    title="Image Resize Plus",
    tags=["image", "resize"],
    category="image",
    version="1.1.0",
)
class ResizeImagePlusInvocation(BaseInvocation):
    """Resizes an image to specific dimensions"""
    image: ImageField = InputField(default=None, description="Image to be resize")
    width: int = InputField(default=512., description="The width to resize to (px)")
    height: int = InputField(default=512., description="The height to resize to (px)")
    resample_mode: PIL_RESAMPLING_MODES = InputField(default="bicubic", description="The resampling mode")
    resize_mod: RESIZE_MODES = InputField(default="fit", description="The resize mode")
    multiple: int = InputField(default=0, description="If set, rounds width and height to nearest multiple of this value")


    def invoke(self, context: InvocationContext) -> ImageOutput:
        RESIZE_MODES_MAP = {
            "fill": self.fill,
            "stretch": self.stretch,
            "fit": self.fit,
            "center": self.center,
            "crop": self.crop,
        }

        image = context.images.get_pil(self.image.image_name)

        resample_mode = PIL_RESAMPLING_MAP[self.resample_mode]
        image_resize = RESIZE_MODES_MAP[self.resize_mod]

        image_out = image_resize(resample_mode, image)

        image_dto = context.images.save(image=image_out)
<<<<<<< HEAD
=======
        
        return ImageOutput.build(image_dto)
>>>>>>> b548f74ad3b014a3d4c58e10ce76a9e0ced8955f
        
        return ImageOutput.build(image_dto)
        

    def __round(self, size: tuple[int, int]) -> tuple[int, int]:
        width, height = size
        if self.multiple > 0:
            def r(v: int) -> int:
                return int(round(v / self.multiple) * self.multiple)
            return r(width), r(height)
        return int(width), int(height)


    def fill(self, resample_mode, image):
        original_width, original_height = image.size
        
        width_ratio = self.width / original_width
        height_ratio = self.height / original_height
        
        resize_ratio = max(width_ratio, height_ratio)
        
        new_width = int(original_width * resize_ratio)
        new_height = int(original_height * resize_ratio)
        new_width, new_height = self.__round((new_width, new_height))

        resized_image = image.resize((new_width, new_height), resample_mode)
        
        final_image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        final_image.paste(resized_image, ((self.width - new_width) // 2, (self.height - new_height) // 2))
        
        return final_image
    


    def stretch(self, resample_mode, image):
        final_image = image.resize((self.width, self.height), resample_mode)
        
        return final_image
    


    def fit(self, resample_mode, image):
        original_width, original_height = image.size

        resize_ratio = original_width / original_height
        width = self.width
        height = self.height

        if (width / height) < resize_ratio:
            height = int(width / resize_ratio)
        else:
            width = int(height * resize_ratio)

        width, height = self.__round((width, height))
        final_image = image.resize((width, height), resample_mode)
        
        return final_image



    def center(self, resample_mode, image):
        original_width, original_height = image.size

        width_ratio = self.width / original_width
        height_ratio = self.height / original_height
        scale_ratio = min(width_ratio, height_ratio)

        new_width = int(scale_ratio * original_width)
        new_height = int(scale_ratio * original_height)
        new_width, new_height = self.__round((new_width, new_height))

        resized_image = image.resize((new_width, new_height), resample_mode)

        final_image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))

        x = (self.width - new_width) // 2
        y = (self.height - new_height) // 2

        final_image.paste(resized_image, (x, y))

        return final_image
    


    def crop(self, resample_mode, image):
        original_width, original_height = image.size
        self.width, self.height = self.__round((self.width, self.height))

        final_image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))

        x = (self.width - original_width) // 2
        y = (self.height - original_height) // 2

        final_image.paste(image, (x, y))

        return final_image
