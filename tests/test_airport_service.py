from app.services.airport_service import AirportService


def main():
    print("=" * 60)
    print("AIRPORT SERVICE TEST")
    print("=" * 60)

    hnd = AirportService.find_by_code("HND")
    sea = AirportService.find_by_code("SEA")
    invalid = AirportService.find_by_code("XXX")

    print("\nHND:")
    print(hnd)

    print("\nSEA:")
    print(sea)

    print("\nInvalid:")
    print(invalid)


if __name__ == "__main__":
    main()