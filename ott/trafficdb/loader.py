

def load_speed_via_cmdline(api_key_required=True, agency_required=True, api_key_msg="Get a TriMet API Key at http://developer.trimet.org/appid/registration"):
    """
    this main() function will call TriMet's GTFS-RT apis by default (as and example of how to load the system)
    """
    args = gtfs_cmdline.gtfs_rt_parser(api_key_required=api_key_required, api_key_msg=api_key_msg, agency_required=agency_required)

    no_errors = load_agency_feeds(session, args.agency_id, aurl, turl, vurl)
    if no_errors:
        log.info("Thinking that loading went well...")
    else:
        log.info("Errors Loading???")


def main():
    load_speed_via_cmdline()


if __name__ == '__main__':
    main()
