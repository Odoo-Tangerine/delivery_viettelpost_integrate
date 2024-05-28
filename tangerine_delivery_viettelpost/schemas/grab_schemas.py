from pydantic import BaseModel, HttpUrl, field_validator
from odoo.addons.tangerine_delivery_base.settings.utils import standardization_e164


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str
    scope: str


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str


class Dimensions(BaseModel):
    height: int
    width: int
    depth: int
    weight: int


class Coordinates(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class Package(BaseModel):
    name: str
    description: str
    quantity: int
    price: int | None = 0
    dimensions: Dimensions


class Quote(BaseModel):
    amount: int


class Location(BaseModel):
    address: str
    coordinates: Coordinates | None | dict = {}


class Contact(BaseModel):
    firstName: str
    email: str | bool | None = None
    phone: str
    smsEnabled: bool = False

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        return standardization_e164(v)


class Schedule(BaseModel):
    pickupTimeFrom: str
    pickupTimeTo: str


class CashOnDelivery(BaseModel):
    amount: float


class DestinationMultiStop(Location):
    packages: list[Package]


class DestinationMultiStopResponse(DestinationMultiStop):
    amount: float


class QuoteMultiStop(BaseModel):
    destination: list[DestinationMultiStopResponse]


class Driver(BaseModel):
    name: str
    phone: str
    licensePlate: str
    photoURL: str
    currentLat: float
    currentLng: float


class DeliveryQuotesRequest(BaseModel):
    serviceType: str | None = None
    vehicleType: str | None = None
    packages: list[Package]
    origin: Location
    destination: Location


class DeliveryQuotesResponse(BaseModel):
    quotes: list[Quote]


class CreateDeliveryRequest(BaseModel):
    merchantOrderID: str
    serviceType: str
    vehicleType: str | None = None
    codType: str | None = None
    paymentMethod: str | None = None
    payer: str | None = None
    highValue: bool
    promoCode: str | None = None
    cashOnDelivery: CashOnDelivery | None = None
    packages: list[Package]
    origin: Location
    destination: Location
    recipient: Contact
    sender: Contact
    schedule: Schedule | None = None


class CreateDeliveryResponse(BaseModel):
    deliveryID: str
    quote: Quote
    trackingURL: str | HttpUrl | None = None


class TrackingWebhookRequest(BaseModel):
    deliveryID: str
    merchantOrderID: str
    status: str
    trackURL: str | HttpUrl | None = None
    failedReason: str | None = None
    driver: Driver | None = None
