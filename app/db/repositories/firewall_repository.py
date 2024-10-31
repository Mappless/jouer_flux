from ipaddress import IPv4Address
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from app.db.models import Firewall
from app.db.session import Session


class FirewallRepository:
    @staticmethod
    def add(firewall: Firewall) -> Firewall:
        with Session() as session:
            session.add(firewall)
            session.commit()
        return firewall

    @staticmethod
    def find_by_ip_address_and_port(
        ip_address: Union[IPv4Address, str], port: int
    ) -> Optional[Firewall]:
        """
        Find a firewall thanks to its ip_address and port.

        :param ip_address: The firewall's IP address
        :param port: The firewall's port

        :return: The firewall if it exists, else return None
        """
        with Session() as session:
            statement = select(Firewall).where(
                Firewall.ip_address == ip_address, Firewall.port == port
            )

            return session.scalar(statement)

    @staticmethod
    def find_by_id(id: int) -> Firewall:
        """
        Find a firewall thanks to its id.

        :param id: The firewall's id

        :raise NoResultFound: if there is no firewall with this id
        """
        with Session() as session:
            return session.get_one(Firewall, id)

    @staticmethod
    def find_by_id_with_filtering_policies(id: int) -> Optional[Firewall]:
        with Session() as session:
            return session.scalar(
                select(Firewall)
                .where(Firewall.id == id)
                .options(
                    joinedload((Firewall._filtering_policies)),
                )
            )

    @staticmethod
    def delete(id: int) -> bool:
        """
        Delete a firewall based on its id.

        :param id: The firewall's id

        :return: True if the firewall was deleted, False if there was none
        """
        with Session() as session:
            try:
                firewall = session.get_one(Firewall, id)
                session.delete(firewall)
                session.commit()

                return True
            except NoResultFound:
                return False
