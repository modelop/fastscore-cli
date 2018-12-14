
from os import remove

class Snapshot(object):
    """
    Represents a snapshot of a model state. Do not create directly. Use the model's snapshots collection:

    >>> model = mm.models['model-1']
    >>> model.snapshots.browse(count=1)
    [{'id': 'yu647a',...}]
    >>> snap = model.snapshots['yu']  # prefix is enough

    """

    def __init__(self, snapid, created_on, stype, size, model):
        self._id = snapid
        self._created_on = created_on
        self._stype = stype
        self._size = size
        self._model = model

    @property
    def id(self):
        """
        A snapshot id.
        """
        return self._id

    @property
    def created_on(self):
        """
        A date the snapshot has been taken.
        """
        return self._created_on

    @property
    def stype(self):
        return self._stype

    @property
    def size(self):
        """
        A size of the snapshot in bytes.
        """
        return self._size

    def to_dict(self):
        return {
            'id': self._id,
            'created_on': self._created_on,
            'stype': self._stype,
            'size': self._size
        }

    def restore(self, engine):
        """
        Restore the model state using the snapshot.

        >>> snap = model.snapshots['yu']  # prefix is enough
        >>> snap.restore(engine)

        """
        tempfile = self._model.download_snapshot(self._id)
        with open(tempfile) as f:
            engine.restore_state(f.read())
        remove(tempfile)

