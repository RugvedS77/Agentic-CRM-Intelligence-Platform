from app.tools.contact_tools import (
    get_contact_profile,
    check_account_status
)

from app.tools.thread_tools import (
    get_thread_history
)


print(
    get_contact_profile(
        "bob.jones@enterprise.net"
    )
)

print(
    check_account_status(
        "bob.jones@enterprise.net"
    )
)

print(
    len(
        get_thread_history(
            "bob.jones@enterprise.net"
        )
    )
)